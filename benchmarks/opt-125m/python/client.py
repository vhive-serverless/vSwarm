import os
import sys
import grpc

from opt_125m_pb2_grpc import Opt125mBenchmarkStub
from opt_125m_pb2 import Opt125mBenchmarkRequest

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = Opt125mBenchmarkStub(channel)
        response = stub.GetBenchmark(Opt125mBenchmarkRequest(regenerate=True))
        print(response)

if __name__ == '__main__':
    run()