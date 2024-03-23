import os
import sys

import tracing
from PIL import Image, ImageOps, ImageFilter

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']

# if LAMBDA is set, then ignore

if not LAMBDA:
    import grpc
    import argparse

    from proto.image_rotate import image_rotate_pb2
    import image_rotate_pb2_grpc

    from concurrent import futures 

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
    parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
    parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
    parser.add_argument("--default_image", default="default.jpg", help="Default image to be rotated if empty")

    args = parser.parse_args()

if tracing.IsTracingEnabled():
    tracing.initTracer("image-rotate-python", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()


def ImageRotateFunction(image_path):
    try:
        img = Image.open(image_path)
        img = img.filter(ImageFilter.BLUR)
        img = img.filter(ImageFilter.MinFilter)
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        img = img.filter(ImageFilter.SHARPEN)
        img = img.transpose(Image.ROTATE_90)
        return f"python.image_rotate.{image_path}"
    except Exception as e:
        return f"python.image_rotate.ImageNotFound.Error:{e}"

if not LAMBDA:
    class ImageRotate(image_rotate_pb2_grpc.ImageRotateServicer):
        def RotateImage(self, request, context):
            if request.name == "":
                imagename = f"images/{args.default_image}"
            else:
                imagename = f"images/{request.name}"
            with tracing.Span("Image Rotate"):
                return_msg = ImageRotateFunction(imagename)
            msg = f"fn: ImageRotate | image: {imagename} | return msg: {return_msg} | runtime: Python"
            return image_rotate_pb2.GetRotatedImage(message=msg)
                
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    image_rotate_pb2_grpc.add_ImageRotateServicer_to_server(ImageRotate(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start ImageRotate-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
