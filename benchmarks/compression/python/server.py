import os
import zlib
import tracing

import grpc
import argparse

from proto.compression import compression_pb2
import compression_pb2_grpc

from concurrent import futures

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
parser.add_argument("--def_file", default="metamorphosis.txt", help="Default file to be compressed if empty")

args = parser.parse_args()

if tracing.IsTracingEnabled():
    tracing.initTracer("compression-python", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()

def FileCompressFunction(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            compressed = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            return f"python.compression.{compressed}"
    except Exception as e:
        return f"python.compression.FileNotFound.Error:{e}"

def FileDecompressFunction(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            decompressed = zlib.decompress(data)
            return decompressed
    except Exception as e:
        return f"python.compression.FileNotFound.Error:{e}"

class CompressFile(compression_pb2_grpc.FileCompressServicer):
    def CompressFile(self, request, context):

        if request.name in ["", "World"]:
            filename = f"{args.def_file}"
        else:
            filename = f"{request.name}"

        try:
            with open(filename):
                pass
        except FileNotFoundError:
            return compression_pb2.CompressedFile(data=f"python.compression.FileNotFound.Error:{filename}".encode())

        with tracing.Span(name="compress_file") as span:
            msg = FileCompressFunction(filename)
        msg = f"fn: CompressFile | file: {filename} | message: {msg} | runtime: Python"
        return compression_pb2.GetCompressedFile(message=msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    compression_pb2_grpc.add_FileCompressServicer_to_server(CompressFile(), server)
    address = f"{args.addr}:{args.port}"
    server.add_insecure_port(address)
    print(f"Starting Python Compression server on {address}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()