# import tracing
from PIL import Image, ImageOps, ImageFilter

from cassandra.cluster import Cluster

from cassandra import DriverException
import shutil
import grpc
import argparse
import os
import logging
from proto.image_rotate import image_rotate_pb2
import image_rotate_pb2_grpc

from concurrent import futures 

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("--default_image", default="default.jpg", help="Default image to be rotated if empty")
parser.add_argument("--db_addr", default="database", help="Cassandra server IP")

args = parser.parse_args()

CACHE_DIR = "./cached_images"
if os.path.exists(CACHE_DIR):
    shutil.rmtree(CACHE_DIR)

os.makedirs(CACHE_DIR, exist_ok=True)

cluster = Cluster([args.db_addr]  ,  protocol_version=5,
    connect_timeout=60,
    control_connection_timeout=60,
    idle_heartbeat_interval=10
)


session = cluster.connect('image_rotate_db')

session.default_timeout = 60




def ImageRotateFunction(image_path,output_image_name):
    try:
        img = Image.open(image_path)
        img = img.filter(ImageFilter.BLUR)
        img = img.filter(ImageFilter.MinFilter)
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        img = img.filter(ImageFilter.SHARPEN)
        img = img.transpose(Image.ROTATE_90)
        img.save(output_image_name)   
        return f"python.image_rotate.{image_path}"
    except Exception as e:
        return f"python.image_rotate.ImageNotFound.Error:{e}"

def fetch_image_from_cassandra(file_name):
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


class ImageRotate(image_rotate_pb2_grpc.ImageRotateServicer):
    def RotateImage(self, request, context):
        imageName = request.name if request.name else args.default_image
        print(imageName)
        image_path = os.path.join(CACHE_DIR, imageName)  
        output_image_name = f"output-{imageName}"
        if not os.path.exists(image_path):
            result = fetch_image_from_cassandra(imageName)
            if not result:
                return image_rotate_pb2.GetRotatedImage(
                    message=f"File not found in Cassandra: {imageName}"
                )
            image_path = result 

        # msg = FileCompressFunction(filename)
        msg = f"fn: CompressFile | file: {imageName} | message: {ImageRotateFunction(image_path,output_image_name)} | runtime: Python"
        return image_rotate_pb2.GetRotatedImage(message=msg)


        # if request.name == "":
        #     imagename = f"{args.default_image}"
        # else:
        #     imagename = f"{request.name}"

        # try:
        #     with open(imagename):
        #         pass
        # except FileNotFoundError:
        #     try:
        #         fs = gridfs.GridFS(db)
        #         image_file_data = fs.find_one({"filename": imagename})
        #         if image_file_data:
        #             with open(imagename, "wb") as file:
        #                 file.write(image_file_data.read())
        #         else:
        #             msg = f"fn: ImageRotate | image: {imagename} | Error: ImageNotFound in GridFS | runtime: Python"
        #             return image_rotate_pb2.GetRotatedImage(message=msg)
        #     except Exception as e:
        #         msg = f"fn: ImageRotate | image: {imagename} | Error: {e} | runtime: Python"
        #         return image_rotate_pb2.GetRotatedImage(message=msg)

        # with tracing.Span("Image Rotate"):
        #     return_msg = ImageRotateFunction(imagename)
        # msg = f"fn: ImageRotate | image: {imagename} | return msg: {return_msg} | runtime: Python"
        # return image_rotate_pb2.GetRotatedImage(message=msg)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    image_rotate_pb2_grpc.add_ImageRotateServicer_to_server(ImageRotate(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    logging.info("Start ImageRotate-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()
