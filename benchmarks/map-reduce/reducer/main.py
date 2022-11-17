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

import logging as log

from reducer import ReduceFunction
from storage import Storage
import tracing

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']

if not LAMBDA:
    import grpc
    import argparse
    import socket

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

if tracing.IsTracingEnabled():
    tracing.initTracer("mapper", url=args.zipkinURL)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()

# constants
S3 = "S3"
XDT = "XDT"

if not LAMBDA:
    class ReducerServicer(mapreduce_pb2_grpc.ReducerServicer):
        def Reduce(self, request, context):
            inputStorage = Storage(request.srcBucket)
            outputStorage = Storage(request.destBucket)

            reduceArgs = {
                'inputStorage' : inputStorage,
                'outputStorage': outputStorage,
                'jobId'     : request.jobId,
                'reducerId' : request.reducerId,
                'nReducers' : request.nReducers,
                'keys'      : [grpc_key.key for grpc_key in request.keys]
            }

            reply = ReduceFunction(reduceArgs)
            return mapreduce_pb2.ReduceReply(
                reply="success"
            )

if LAMBDA:
    class AWSLambdaReducerServicer:
        def Reduce(self, event, context):
            inputStorage = Storage(event["srcBucket"])
            outputStorage = Storage(event["destBucket"])

            reduceArgs = {
                'inputStorage' : inputStorage,
                'outputStorage': outputStorage,
                'jobId'     : event["jobId"],
                'reducerId' : event["reducerId"],
                'nReducers' : event["nReducers"],
                'keys'      : event['keys'].split(',')
            }

            return ReduceFunction(reduceArgs)


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
    mapreduce_pb2_grpc.add_ReducerServicer_to_server(ReducerServicer(), server)
    server.add_insecure_port('[::]:' + args.sp)
    server.start()
    server.wait_for_termination()


def lambda_handler(event, context):
    reducerServicer = AWSLambdaReducerServicer()
    return reducerServicer.Reduce(event, context)

if __name__ == '__main__' and not LAMBDA:
    log.basicConfig(level=log.INFO)
    serve()
