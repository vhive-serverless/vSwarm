import os
import sys
import grpc

from gptj_pb2_grpc import GptJBenchmarkStub
from gptj_pb2 import GptJBenchmarkRequest

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = GptJBenchmarkStub(channel)
        print("hello client")
        response = stub.GetBenchmark(GptJBenchmarkRequest(regenerate=False))
        print(response)

if __name__ == '__main__':
    run()