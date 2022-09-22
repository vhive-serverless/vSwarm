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

import os
import resource
import sys
import time

import boto3
import json
import logging as log
import pickle

LAMBDA = os.environ.get('IS_LAMBDA', 'yes').lower() in ['true', 'yes', '1']
TRACE = os.environ.get('TRACING_ON', 'no').lower() in ['true', 'yes', '1', 'on']

if not LAMBDA:
	import grpc
	import argparse
	import socket
	from joblib import Parallel, delayed

	import mapreduce_pb2_grpc
	import mapreduce_pb2
	import destination as XDTdst
	import source as XDTsrc
	import utils as XDTutil

	from concurrent import futures

	parser = argparse.ArgumentParser()
	parser.add_argument("-dockerCompose", "--dockerCompose",
		dest="dockerCompose", default=False, help="Env docker compose")
	parser.add_argument("-sp", "--sp", dest="sp", default="80", help="serve port")
	parser.add_argument("-zipkin", "--zipkin", dest="zipkinURL",
		default="http://zipkin.istio-system.svc.cluster.local:9411/api/v2/spans",
		help="Zipkin endpoint url")

	args = parser.parse_args()

if TRACE:
	# adding python tracing sources to the system path
	sys.path.insert(0, os.getcwd() + '/../proto/')
	sys.path.insert(0, os.getcwd() + '/../../../utils/tracing/python')

	import tracing

	if tracing.IsTracingEnabled():
		tracing.initTracer("reducer", url=args.zipkinURL)
		tracing.grpcInstrumentClient()
		tracing.grpcInstrumentServer()

# constants
INPUT_MAPPER_PREFIX = "artemiy/"
OUTPUT_MAPPER_PREFIX = "artemiy/task/mapper/"
INPUT_REDUCER_PREFIX = OUTPUT_MAPPER_PREFIX
OUTPUT_REDUCER_PREFIX = "artemiy/task/reducer/"
S3 = "S3"
XDT = "XDT"

# set aws credentials:
AWS_ID = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET = os.getenv('AWS_SECRET_KEY')

S3CLIENT = boto3.resource(
	service_name='s3',
	region_name=os.getenv("AWS_REGION", 'us-west-1'),
	aws_access_key_id=AWS_ID,
	aws_secret_access_key=AWS_SECRET
)

if not LAMBDA:
	class ReducerServicer(mapreduce_pb2_grpc.ReducerServicer):
		def __init__(self, transferType, XDTconfig=None):
			self.transferType = transferType
			self.s3_client = S3CLIENT
			if transferType == XDT:
				if XDTconfig is None:
					log.fatal("Empty XDT config")
				self.XDTclient = XDTsrc.XDTclient(XDTconfig)
				self.XDTconfig = XDTconfig

		def put(self, bucket, key, obj, metadata=None, forceS3=False):
			msg = "Reducer uploading object with key '" + key + "' to " + self.transferType
			log.info(msg)
			with tracing.Span(msg):
				if self.transferType == S3 or forceS3:
					s3object = self.s3_client.Object(bucket_name=bucket, key=key)
					if metadata is None:
						s3object.put(Body=obj)
					else:
						s3object.put(Body=obj, Metadata=metadata)
				elif self.transferType == XDT:
					key = self.XDTclient.Put(payload=obj)

			return key

		def get(self, bucket, key):
			msg = "Reducer gets key '" + key + "' from " + self.transferType
			log.info(msg)
			with tracing.Span(msg):
				if self.transferType == S3:
					obj = self.s3_client.Object(bucket_name=bucket, key=key)
					response = obj.get()
					return response['Body'].read()
				elif self.transferType == XDT:
					return XDTdst.Get(key, self.XDTconfig)

		def Reduce(self, request, context):
			start_time = time.time()
			r_id = request.reducerId
			log.info(f"Reducer {r_id} is invoked")

			dest_bucket = request.destBucket  # s3 bucket where the mapper will write the result
			src_bucket = request.srcBucket   # s3 bucket where the mapper will search for input files
			reducer_keys = request.keys       # reducer_keys is a list of input file names for this mapper
			job_id = request.jobId
			n_reducers = request.nReducers

			# aggr
			results = {}
			line_count = 0

			# INPUT JSON => OUTPUT JSON

			# Download and process all keys
			responses = []
			with tracing.Span("Fetch keys"):
				read_tasks = []
				for grpc_key in reducer_keys:
					key = grpc_key.key
					# key = INPUT_REDUCER_PREFIX + "job_" + job_id + "/shuffle_" + str(r_id) + "/" + key
					read_tasks.append((src_bucket, key))
				responses = Parallel(backend="threading", n_jobs=len(read_tasks))(delayed(self.get)(*i) for i in read_tasks)

			time_in_secs = 0
			start_time = time.time()

			with tracing.Span("Compute reducer result"):
				for response in responses:
					try:
						for srcIp, val in pickle.loads(response).items():
							line_count +=1
							if srcIp not in results:
								results[srcIp] = 0
							results[srcIp] += float(val)
					except:
						e = sys.exc_info()[0]
						print(e)

				time_in_secs += (time.time() - start_time)

				pret = [len(reducer_keys), line_count, time_in_secs]
				print ("Reducer" + str(r_id), pret)

			with tracing.Span("Save result"):
				if n_reducers == 1:
					fname = "%sjob_%s/result" % (OUTPUT_REDUCER_PREFIX, job_id)
				else:
					fname = "%sjob_%s/reducer_%s" % (OUTPUT_REDUCER_PREFIX, job_id, r_id)

				metadata = {
					"linecount":  '%s' % line_count,
					"processingtime": '%s' % time_in_secs,
					"memoryUsage": '%s' % resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
				}

				self.put(dest_bucket, fname, pickle.dumps(results), metadata=metadata, forceS3=True)

			return mapreduce_pb2.ReduceReply(
				reply="success"
			)


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
	mapreduce_pb2_grpc.add_ReducerServicer_to_server(
		ReducerServicer(transferType=transferType, XDTconfig=XDTconfig), server)
	server.add_insecure_port('[::]:' + args.sp)
	server.start()
	server.wait_for_termination()


def lambda_handler(event, context):
	outputReducerPrefix = os.environ.get('OUTPUT_MAPPER_PREFIX', "artemiy/task/mapper/")
	obj = Storage("S3", event['srcBucket'])

	responses = []
	keys = event['keys'].split(',')
	for key in keys:
		responses.append(obj.get(key))

	results = {}
	line_count = 0
	for resp in responses:
		try:
			for srcIp, val in pickle.loads(resp).items():
				line_count += 1
				if srcIp not in results:
					results[srcIp] = 0
				results[srcIp] += float(val)
		except:
			print(sys.exc_info())

	reduceKey = "%sjob_0/reducer_%s" % (outputReducerPrefix, event['reducerId'])
	metadata = {
		"linecount":  str(line_count),
		"processingtime": str(time_in_secs),
		"memoryUsage": str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
	}
	obj.put(reduceKey, pickle.dumps(results), metadata)

	return {
		'reply' : "success"
	}

if __name__ == '__main__' and not LAMBDA:
	log.basicConfig(level=log.INFO)
	serve()
