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
from proto.graph_bfs import graph_bfs_pb2
import graph_bfs_pb2_grpc

import os
import sys

import random
import time
import igraph

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
    tracing.initTracer("graph_bfs", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()

def graph_bfs(dur):
    """
    Builds a large random graph and performs random BFS traversals for the specified duration (in milliseconds).
    Returns the number of BFS traversals performed.
    """
    # Parameters for a massive graph (adjust as needed for your system's memory)
    num_vertices = 100000  # 100k nodes
    num_edges = 1000000    # 1M edges

    # Build a random graph
    g = igraph.Graph.Erdos_Renyi(n=num_vertices, m=num_edges, directed=False)

    start_time = time.time()
    bfs_count = 0
    dur_sec = dur / 1000.0

    while (time.time() - start_time) < dur_sec:
        root = random.randint(0, num_vertices - 1)
        # Perform BFS from a random root
        _ = g.bfs(root)
        bfs_count += 1

    return bfs_count


class GraphBFSBenchmark(graph_bfs_pb2_grpc.GraphBFSBenchmarkServicer):

    def GetBfs(self, request, context):
        with tracing.Span("Run graph_bfs"):
            dur = int(request.name)         # Duration the function must run for in milliseconds
            bfs_count = graph_bfs(dur)

        gid = syscall(104)
        msg = f"fn: graph_bfs | duration_ms: {dur} | bfs_count: {bfs_count} | runtime: python"
        return graph_bfs_pb2.GraphBFSBenchmarkReply(message=msg)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    graph_bfs_pb2_grpc.add_GraphBFSBenchmarkServicer_to_server(GraphBFSBenchmark(), server)

    address = ('[::]:' + GRPC_PORT_ADDRESS if GRPC_PORT_ADDRESS else  '[::]:50051')
    server.add_insecure_port(address) 

    logging.info("Start server: listen on : " + address)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
