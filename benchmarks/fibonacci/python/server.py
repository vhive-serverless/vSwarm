#!/bin/python3

from concurrent import futures
import logging
import argparse

import grpc
import string

import helloworld_pb2
import helloworld_pb2_grpc

# adding python tracing sources to the system path
sys.path.insert(0, os.getcwd() + '/../../../../utils/tracing/python')
import tracing

import os
import sys
import ctypes
libc = ctypes.CDLL(None)
syscall = libc.syscall

print("python version: %s" % sys.version)
print("Server has PID: %d" % os.getpid())
GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")

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



class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):

        with tracing.Span("Run fibonacci"):
            x = int(request.name)
            y = fibonacci(x)

        gid = syscall(104)
        msg = "Hello: this is GID: %i Invoke python fib: y = fib(x) | x: %i y: %.1f" % (gid,x,y)
        return helloworld_pb2.HelloReply(message=msg)

def get_address():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--server', type=str, default='[::]')
    parser.add_argument('-p', '--port', type=int, default=50051)
    args = parser.parse_args()
    # In case one define the address with http prefix, remove it.
    server, port = args.server, args.port
    prefix = 'http://'
    server = server[len(prefix):] if server.startswith(prefix) else server
    port = (int(GRPC_PORT_ADDRESS) if GRPC_PORT_ADDRESS else port)
    return "%s:%i" % (server, port)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    address = get_address()
    server.add_insecure_port(address)
    print("Before compile")
    print("Start server: listen on : " + address)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
