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

from concurrent import futures
import logging
import argparse

import grpc
import string

from proto.fibonacci import fibonacci_pb2
import fibonacci_pb2_grpc

import os
import sys

# adding python tracing sources to the system path
sys.path.insert(0, os.getcwd() + '/../../../../utils/tracing/python')
import tracing

import ctypes
libc = ctypes.CDLL(None)
syscall = libc.syscall

print("python version: %s" % sys.version)
print("Server has PID: %d" % os.getpid())
GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
args = parser.parse_args()

if tracing.IsTracingEnabled():
    tracing.initTracer("fibonacci", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()

sys.set_int_max_str_digits(500000)

def fibonacci(num):
    num1=0
    num2=1
    sum=0
    for i in range(num):
        sum=num1+num2
        num1=num2
        num2=sum
    return num1



class Greeter(fibonacci_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):

        with tracing.Span("Run fibonacci"):
            x = int(request.name)
            y = fibonacci(x)

        gid = syscall(104)
        msg = "fn: Fib: y = fib(x) | x: %i y: %i | runtime: python" % (x,y)
        return fibonacci_pb2.HelloReply(message=msg)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    fibonacci_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    address = ('[::]:' + GRPC_PORT_ADDRESS if GRPC_PORT_ADDRESS else  '[::]:50051')
    server.add_insecure_port(address) 

    logging.info("Start server: listen on : " + address)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
