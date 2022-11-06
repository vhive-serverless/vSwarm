#!/bin/python3

# MIT License

# Copyright (c) 2022 EASE lab

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys

import logging

import tracing

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']
TRACE = os.environ.get('ENABLE_TRACING', 'no').lower() in ['true', 'yes', '1', 'on']

if not LAMBDA:
    import grpc
    import argparse

    from proto.fibonacci import fibonacci_pb2
    import fibonacci_pb2_grpc

    from concurrent import futures

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
    parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
    parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
    args = parser.parse_args()

    GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")

if TRACE:
    # adding python tracing sources to the system path
    sys.path.insert(0, os.getcwd() + '/../../../../utils/tracing/python')
    if tracing.IsTracingEnabled():
        tracing.initTracer("fibonacci", url=args.url)
        tracing.grpcInstrumentClient()
        tracing.grpcInstrumentServer()

def fibonacci(num):
    num1=0
    num2=1
    sum=0
    for i in range(num):
        sum=num1+num2
        num1=num2
        num2=sum
    return num1

if not LAMBDA:
    class Greeter(fibonacci_pb2_grpc.GreeterServicer):
        def SayHello(self, request, context):
            with tracing.Span("Run fibonacci"):
                x = int(request.name)
                y = fibonacci(x)
            msg = "fn: Fib: y = fib(x) | x: %i y: %i | runtime: python" % (x,y)
            return fibonacci_pb2.HelloReply(message=msg)

if LAMBDA:
    class Fibonacci():
        def compute(self, x):
            y = fibonacci(x)
            msg = "fn: Fib: y = fib(x) | x: %i y: %i | runtime: python" % (x,y)
            return msg

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    fibonacci_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    address = ('[::]:' + GRPC_PORT_ADDRESS if GRPC_PORT_ADDRESS else  '[::]:50051')
    server.add_insecure_port(address)
    logging.info("Start server: listen on : " + address)
    server.start()
    server.wait_for_termination()

def lambda_handler(event, context):
    fibObj = Fibonacci()
    return fibObj.compute(int(event['name']))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
