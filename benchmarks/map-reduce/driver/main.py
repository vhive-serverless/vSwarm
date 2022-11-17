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
import sys

from concurrent import futures
import logging as log

import tracing
from driver import DriveFunction

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']

if LAMBDA:
    import boto3
    import json

if not LAMBDA:
    import grpc
    from grpc_reflection.v1alpha import reflection
    import argparse

    import helloworld_pb2_grpc
    import helloworld_pb2
    import mapreduce_pb2_grpc
    import mapreduce_pb2

    parser = argparse.ArgumentParser()
    parser.add_argument("-dockerCompose", "--dockerCompose",
        dest="dockerCompose", default=False, help="Env docker compose")
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

if tracing.IsTracingEnabled():
    tracing.initTracer("driver", url=args.zipkinURL)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()

# constants
S3 = "S3"

if not LAMBDA:
    class GreeterServicer(helloworld_pb2_grpc.GreeterServicer):
        def call_mapper(self, arg: dict):
            log.info(f"Invoking Mapper {arg['mapperId']}")
            channel = grpc.insecure_channel(args.mAddr)
            stub = mapreduce_pb2_grpc.MapperStub(channel)

            req = mapreduce_pb2.MapRequest(
                srcBucket = arg["srcBucket"],
                destBucket = arg["destBucket"],
                jobId = arg["jobId"],
                mapperId = arg["mapperId"],
                nReducers = arg["nReducers"]
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

        def prepareReduceKeys(self, all_result_futures, NUM_REDUCERS):
            reduce_input_keys = {}
            for i in range(NUM_REDUCERS):
                reduce_input_keys[i] = []

            #this is just to wait for all futures to complete
            for result_keys in all_result_futures:
                for i in range(NUM_REDUCERS):
                    reduce_input_keys[i].append(result_keys[i].key)

            return reduce_input_keys

        # Driver code below
        def SayHello(self, request, context):
            driverArgs = {
                'callMapperMethod'  : self.call_mapper,
                'callReducerMethod' : self.call_reducer,
                'prepareReduceKeys' : self.prepareReduceKeys
            }

            DriveFunction(driverArgs)
            return helloworld_pb2.HelloReply(message="jobs done")

if LAMBDA:
    class AWSLambdaDriverServicer:
        def __init__(self):
            self.lambda_client = boto3.client("lambda")

        def call_mapper(self, mapperArgs: dict):
            log.info(f"Invoking Mapper {mapperArgs['mapperId']}")
            mapperArgs['keys'] = ','.join(mapperArgs['keys'])

            response = self.lambda_client.invoke(
                FunctionName = os.environ.get('MAPPER_FUNCTION', 'mapper'),
                InvocationType = 'RequestResponse',
                LogType = 'None',
                Payload = json.dumps(mapperArgs),
            )
            payloadBytes = response['Payload'].read()
            payloadJson = json.loads(payloadBytes)
            log.info(f"Mapper Reply {payloadJson}")

            return payloadJson

        def call_reducer(self, reducerArgs: dict):
            log.info(f"Invoking Mapper {reducerArgs['reducerId']}")

            response = self.lambda_client.invoke(
                FunctionName = os.environ.get('REDUCER_FUNCTION', 'reducer'),
                InvocationType = 'RequestResponse',
                LogType = 'None',
                Payload = json.dumps(reducerArgs),
            )
            payloadBytes = response['Payload'].read()
            payloadJson = json.loads(payloadBytes)
            log.info(f"Reducer Reply {payloadJson}")

        def prepareReduceKeys(self, all_result_futures, NUM_REDUCERS):
            reduce_input_keys = {}
            for i in range(NUM_REDUCERS):
                reduce_input_keys[i] = ''

            #this is just to wait for all futures to complete
            for result_keys in all_result_futures:
                for i in range(NUM_REDUCERS):
                    if reduce_input_keys[i] == '':
                        reduce_input_keys[i] += result_keys['keys'][i]
                    else:
                        reduce_input_keys[i] += ',' + result_keys['keys'][i]


            return reduce_input_keys

        def SayHello(self, request, context):
            driverArgs = {
                'callMapperMethod'  : self.call_mapper,
                'callReducerMethod' : self.call_reducer,
                'prepareReduceKeys' : self.prepareReduceKeys
            }

            DriveFunction(driverArgs)
            return "jobs done"

def serve():
    max_workers = int(os.getenv("MAX_SERVER_THREADS", 16))
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(GreeterServicer(), server)
    SERVICE_NAMES = (
        helloworld_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port('[::]:' + args.sp)
    server.start()
    server.wait_for_termination()

def lambda_handler(event, context):
    driverServicer = AWSLambdaDriverServicer()
    return driverServicer.SayHello(event, context)

if __name__ == '__main__':
    log.basicConfig(level=log.INFO)
    serve()
