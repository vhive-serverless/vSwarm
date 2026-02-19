import os
import zlib
# import tracing

# from pymongo import MongoClient
# import gridfs
from cassandra.cluster import Cluster
import logging
from cassandra import DriverException
import grpc
import argparse
import shutil

from proto.compression import compression_pb2
import compression_pb2_grpc

from concurrent import futures

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="Server IP")
parser.add_argument("-p", "--port", dest="port", default="50051", help="Server port")
parser.add_argument("--def_file", default="metamorphosis.txt", help="Default file to be compressed if empty")
parser.add_argument("--db_addr", default="database", help="Cassandra server IP")
args = parser.parse_args()



CACHE_DIR = "./cached_files"
if os.path.exists(CACHE_DIR):
    shutil.rmtree(CACHE_DIR)

os.makedirs(CACHE_DIR, exist_ok=True)

cluster = Cluster([args.db_addr]  ,  protocol_version=5,
    connect_timeout=60,
    control_connection_timeout=60,
    idle_heartbeat_interval=10
)

session = cluster.connect('compression_db')

session.default_timeout = 60


def FileCompressFunction(file_path,output_file_name):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            compressed = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            with open(output_file_name, "wb") as out:
                out.write(compressed)
            return f"python.compression.{file_path}"
    except Exception as e:
        return f"python.compression.FileNotFound.Error:{e}"

def FileDecompressFunction(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            decompressed = zlib.decompress(data)
            return f"python.decompression.{file_path}"
    except Exception as e:
        return f"python.compression.FileNotFound.Error:{e}"


def fetch_file_from_cassandra(file_name):
    cached_path = os.path.join(CACHE_DIR, file_name)
    if os.path.exists(cached_path):
        return cached_path
    # print(video_name)
    try:
        row = session.execute(
            "SELECT file_id FROM files WHERE filename = %s",
            (file_name,)
        ).one()
    except DriverException as e:
        print("Error fetching file_id:", e)
        return None

    file_id = row.file_id
    chunks = session.execute(
        "SELECT data FROM chunks WHERE file_id=%s ORDER BY chunk_index  ALLOW FILTERING", 
        (file_id,)
    )

    with open(cached_path, "wb") as f:
        for chunk in chunks:
            f.write(chunk.data)
    print("edw 1")
    return cached_path

class CompressFile(compression_pb2_grpc.FileCompressServicer):
    def CompressFile(self, request, context):

        filename = request.name if request.name else args.def_file
        print(filename)
        file_path = os.path.join(CACHE_DIR, filename)  
        output_file_name = f"output-{filename}.zlib"
        if not os.path.exists(file_path):
            result = fetch_file_from_cassandra(filename)
            if not result:
                return compression_pb2.GetCompressedFile(
                    message=f"File not found in Cassandra: {filename}"
                )
            file_path = result 

        # msg = FileCompressFunction(filename)
        msg = f"fn: CompressFile | file: {filename} | message: {FileCompressFunction(file_path,output_file_name)} | runtime: Python"
        return compression_pb2.GetCompressedFile(message=msg)
        
        # try:
        #     with open(filename):
        #         pass
        # except FileNotFoundError:
        #     try:
        #         fs = gridfs.GridFS(db)
        #         file_data = fs.find_one({"filename": filename})
        #         if file_data:
        #             with open(filename, "wb") as file:
        #                 file.write(file_data.read())
        #         else:
        #             msg = f"fn: CompressFile | file: {filename} | Error: FileNotFound in GridFS | runtime: Python"
        #             return compression_pb2.GetCompressedFile(message=msg)
        #     except Exception as e:
        #         msg = f"fn: CompressFile | file: {filename} | Error: {e} | runtime: Python"
        #         return compression_pb2.GetCompressedFile(message=msg)

        # with tracing.Span(name="compress_file") as span:
        #     msg = FileCompressFunction(filename)
        # msg = f"fn: CompressFile | file: {filename} | message: {msg} | runtime: Python"
        # return compression_pb2.GetCompressedFile(message=msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    compression_pb2_grpc.add_FileCompressServicer_to_server(CompressFile(), server)
    address = f"{args.addr}:{args.port}"
    server.add_insecure_port(address)
    logging.info("Start server: listen on : " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)    
    serve()