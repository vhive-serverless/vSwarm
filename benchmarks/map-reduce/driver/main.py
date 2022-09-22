# MIT License
#
# Copyright (c) 2021 Michal Baczun and EASE lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import os

import boto3
import json
import logging as log
from concurrent import futures

LAMBDA = os.environ.get('IS_LAMBDA', 'yes').lower() in ['true', 'yes', '1']
TRACE = os.environ.get('TRACING_ON', 'no').lower() in ['true', 'yes', '1', 'on']

if not LAMBDA:
	import helloworld_pb2_grpc
	import helloworld_pb2
	import mapreduce_pb2_grpc
	import mapreduce_pb2
	import destination as XDTdst
	import source as XDTsrc
	import utils as XDTutil

	import grpc
	from grpc_reflection.v1alpha import reflection
	import argparse
	import socket
	import resource
	from io import StringIO ## for Python 3
	import time
	from joblib import Parallel, delayed

	parser = argparse.ArgumentParser()
	parser.add_argument("-dockerCompose", "--dockerCompose", dest="dockerCompose",
		default=False, help="Env docker compose")
	parser.add_argument("-mAddr", "--mAddr", dest="mAddr",
		default="mapper.default.192.168.1.240.sslip.io:80",
		help="trainer address")
	parser.add_argument("-rAddr", "--rAddr", dest="rAddr",
		default="reducer.default.192.168.1.240.sslip.io:80",
		help="reducer address")
	parser.add_argument("-sp", "--sp", dest="sp", default="80",
		help="serve port")
	parser.add_argument("-zipkin", "--zipkin", dest="zipkinURL",
		default="http://zipkin.istio-system.svc.cluster.local:9411/api/v2/spans",
		help="Zipkin endpoint url")

	args = parser.parse_args()

if TRACE:
	import tracing

	if tracing.IsTracingEnabled():
		tracing.initTracer("driver", url=args.zipkinURL)
		tracing.grpcInstrumentClient()
		tracing.grpcInstrumentServer()

# constants
INPUT_MAPPER_PREFIX = "artemiy/"
OUTPUT_MAPPER_PREFIX = "artemiy/task/mapper/"
INPUT_REDUCER_PREFIX = OUTPUT_MAPPER_PREFIX
OUTPUT_REDUCER_PREFIX = "artemiy/task/reducer/"
S3 = "S3"
XDT = "XDT"
NUM_MAPPERS = int(os.environ.get('NUM_MAPPERS', "1"))  # can't be more than 2215
NUM_REDUCERS = int(os.environ.get('NUM_REDUCERS', "1")) # must be power of 2 and smaller than NUM_MAPPERS

# set aws credentials
AWS_ID = os.getenv('AWS_ACCESS_KEY', "")
AWS_SECRET = os.getenv('AWS_SECRET_KEY', "")

if LAMBDA:
	lambda_client = boto3.client("lambda")


def prepare_map_tasks():
	map_ev = {
		"srcBucket": "storage-module-test",
		"destBucket": "storage-module-test",
		"jobId": "0",
		"mapperId": 0,
		"nReducers": NUM_REDUCERS,
	}

	map_tasks = []
	for i in range(NUM_MAPPERS):
		map_tasks.append(map_ev.copy())
		map_tasks[i]['mapperId'] = i
		if not LAMBDA:
			map_tasks[i]['keys'] = ["part-" + str(i).zfill(5)]
		elif 'keys' not in map_tasks[i]:
			map_tasks[i]['keys'] = "part-" + str(i).zfill(5)
		else:
			map_tasks[i]['keys'] += ",part-" + str(i).zfill(5)

	return map_tasks


def prepare_reduce_tasks(reduce_input_keys):
	reduce_ev = {
		"srcBucket": "storage-module-test",
		"destBucket": "storage-module-test",
		"nReducers": NUM_REDUCERS,
		"jobId": "0",
		"reducerId": 0,
	}

	reducer_tasks = []
	for i in range(NUM_REDUCERS):
		log.info("assigning keys to reducer %d", i)
		log.info(reduce_input_keys[i])
		reduce_ev["keys"] = reduce_input_keys[i]
		reducer_tasks.append(reduce_ev.copy())
		reducer_tasks[i]['reducerId'] = i

	return reducer_tasks

def drive_map(mapper_invoker):
	map_tasks = prepare_map_tasks()

	mapper_responses=[]
	ex = futures.ThreadPoolExecutor(max_workers=NUM_MAPPERS)
	all_result_futures = ex.map(mapper_invoker, map_tasks)

	reduce_input_keys = {}
	for i in range(NUM_REDUCERS):
		if not LAMBDA:
			reduce_input_keys[i] = []
		else:
			reduce_input_keys[i] = ''

	#this is just to wait for all futures to complete
	for result_keys in all_result_futures:
		for i in range(NUM_REDUCERS):
			if not LAMBDA:
				reduce_input_keys[i].append(result_keys[i].key)
			elif reduce_input_keys[i] == '':
				reduce_input_keys[i] += result_keys['keys'][i]
			else:
				reduce_input_keys[i] += ',' + result_keys['keys'][i]


	return reduce_input_keys

def drive_reduce(reduce_input_keys, reduce_invoker):
	reducer_tasks = prepare_reduce_tasks(reduce_input_keys)

	reducer_responses=[]
	ex = futures.ThreadPoolExecutor(max_workers=NUM_REDUCERS)
	all_result_futures = ex.map(reduce_invoker, reducer_tasks)

	for result in all_result_futures:
		reducer_responses.append(result)

	return reducer_responses

if not LAMBDA:
	class GreeterServicer(helloworld_pb2_grpc.GreeterServicer):
		def __init__(self, transferType, XDTconfig=None):
			self.transferType = transferType
			if transferType == S3:
				self.s3_client = boto3.resource(
					service_name='s3',
					region_name=os.getenv("AWS_REGION", 'us-west-1'),
					aws_access_key_id=AWS_ID,
					aws_secret_access_key=AWS_SECRET
				)
			elif transferType == XDT:
				if XDTconfig is None:
					log.fatal("Empty XDT config")
				self.XDTclient = XDTsrc.XDTclient(XDTconfig)
				self.XDTconfig = XDTconfig

		def put(self, bucket, key, obj, metadata=None):
			msg = "Driver uploading object with key '" + key + "' to " + self.transferType
			log.info(msg)
			with tracing.Span(msg):
				if self.transferType == S3:
					s3object = self.s3_client.Object(bucket_name=bucket, key=key)
					if metadata is None:
						s3object.put(Body=obj)
					else:
						s3object.put(Body=obj, Metadata=metadata)
				elif self.transferType == XDT:
					key = self.XDTclient.Put(payload=obj)

			return key

		def get(self, key):
			msg = "Driver gets key '" + key + "' from " + self.transferType
			log.info(msg)
			with tracing.Span(msg):
				response = None
				if self.transferType == S3:
					obj = self.s3_client.Object(bucket_name=self.benchName, key=key)
					response = obj.get()
				elif self.transferType == XDT:
					return XDTdst.Get(key, self.XDTconfig)

			return response['Body'].read()

		def call_mapper(self, arg: dict):
			log.info(f"Invoking Mapper {arg['mapperId']}")
			channel = grpc.insecure_channel(args.mAddr)
			stub = mapreduce_pb2_grpc.MapperStub(channel)

			req = mapreduce_pb2.MapRequest(
				srcBucket = arg["srcBucket"],
				destBucket = arg["destBucket"],
				jobId = arg["jobId"],
				mapperId = arg["mapperId"],
				nReducers = arg["nReducers"],
			)
			for key_string in arg["keys"]:
				grpc_keys = mapreduce_pb2.Keys()
				grpc_keys.key = key_string
				req.keys.append(grpc_keys)

			resp = stub.Map(req)
			log.info(f"mapper reply: {resp}")
			return resp.keys

		def call_reducer(self, arg: dict):
			log.info(f"Invoking Reducer {arg['reducerId']}")
			channel = grpc.insecure_channel(args.rAddr)
			stub = mapreduce_pb2_grpc.ReducerStub(channel)

			req = mapreduce_pb2.ReduceRequest(
				srcBucket = arg["srcBucket"],
				destBucket = arg["destBucket"],
				jobId = arg["jobId"],
				reducerId = arg["reducerId"],
				nReducers = arg["nReducers"],
			)
			for key_string in arg["keys"]:
				grpc_keys = mapreduce_pb2.Keys()
				grpc_keys.key = key_string
				req.keys.append(grpc_keys)

			resp = stub.Reduce(req)
			log.info(f"reducer reply: {resp}")

		# Driver code below
		def SayHello(self, request, context):
			log.info("Driver received a request")

			reduce_input_keys = drive_map(self.call_mapper)
			log.info("calling mappers done")

			reducer_responses = drive_reduce(reduce_input_keys, self.call_reducer)
			log.info("calling reducers done")

			return helloworld_pb2.HelloReply(message="jobs done")


def serve():
	transferType = os.getenv('TRANSFER_TYPE', S3)

	XDTconfig = dict()
	if transferType == XDT:
		XDTconfig = XDTutil.loadConfig()
		log.info("XDT config:")
		log.info(XDTconfig)

	log.info("Using inline or s3 transfers")
	max_workers = int(os.getenv("MAX_SERVER_THREADS", 16))
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
	helloworld_pb2_grpc.add_GreeterServicer_to_server(
		GreeterServicer(transferType=transferType, XDTconfig=XDTconfig), server)
	SERVICE_NAMES = (
		helloworld_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
		reflection.SERVICE_NAME,
	)
	reflection.enable_server_reflection(SERVICE_NAMES, server)
	server.add_insecure_port('[::]:' + args.sp)
	server.start()
	server.wait_for_termination()

def call_lambda_mapper(mapperArgs: dict):
	response = lambda_client.invoke(
		FunctionName = os.environ.get('MAPPER_FUNCTION', 'mapper'),
		InvocationType = 'RequestResponse',
		LogType = 'None',
		Payload = json.dumps(mapperArgs),
	)
	payloadBytes = response['Payload'].read()
	payloadJson = json.loads(payloadBytes)

	return payloadJson

def call_lambda_reduce(reducerArgs: dict):
	response = lambda_client.invoke(
		FunctionName = os.environ.get('REDUCER_FUNCTION', 'reducer'),
		InvocationType = 'RequestResponse',
		LogType = 'None',
		Payload = json.dumps(reducerArgs),
	)
	payloadBytes = response['Payload'].read()
	payloadJson = json.loads(payloadBytes)

	return payloadJson

def lambda_handler(event, context):
	log.basicConfig(level=log.INFO)
	log.info("Driver received a request")

	global NUM_MAPPERS, NUM_REDUCERS

	if "NUM_MAPPERS" in event:
		NUM_MAPPERS = int(event['NUM_MAPPERS'])
	if "NUM_REDUCERS" in event:
		NUM_REDUCERS = int(event['NUM_REDUCERS'])

	reduce_input_keys = drive_map(call_lambda_mapper)
	log.info("calling mappers done")
	reduce_results = drive_reduce(reduce_input_keys, call_lambda_reduce)


	return "All Jobs Done"

if __name__ == '__main__' and not LAMBDA:
	log.basicConfig(level=log.INFO)
	serve()
