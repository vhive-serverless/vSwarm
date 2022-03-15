from concurrent import futures
import logging

import grpc

import random
import string
import pyaes

import argparse
import os
import sys

# For local builds add protobuffer and
# python tracing sources to the system path
sys.path.insert(0, os.getcwd() + '/../proto')
import helloworld_pb2
import helloworld_pb2_grpc

sys.path.insert(0, os.getcwd() + '/../../../utils/tracing/python')
import tracing

# USE ENV VAR "DecoderFrames" to set the number of frames to be sent
parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
parser.add_argument("-k", "--key", dest="KEY", default="6368616e676520746869732070617373", help="Secret key")
parser.add_argument("--default_plaintext", default="exampleplaintext", help="Default plain text if name is empty or 'world'")
args = parser.parse_args()


if tracing.IsTracingEnabled():
    tracing.initTracer("aes-python", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()


def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

KEY = args.KEY.encode(encoding = 'UTF-8')
message = generate(100)

from base64 import b64decode

def AESModeCTR(plaintext):
    counter = pyaes.Counter(initial_value = 0)
    aes = pyaes.AESModeOfOperationCTR(KEY, counter = counter)
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

def AESModeCBC(plaintext):
    # random initialization vector of 16 bytes
    # blocks_size = 16
    iv = "InitializationVe"
    pad = 16 - len(plaintext)% blocks_size
    plaintext = str("0" * pad) + plaintext
    aes = pyaes.AESModeOfOperationCBC(KEY, iv = iv)
    ciphertext = aes.encrypt(plaintext)

    print(ciphertext, ciphertext.decode('UTF-8'))

    return ciphertext.decode('UTF-8')


class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):

        if request.name in ["", "world"]:
            plaintext = args.default_plaintext
        else:
            plaintext = request.name

        with tracing.Span("AES Encryption"):
            ciphertext = AESModeCTR(plaintext)

        msg = f"fn: AES | plaintext: {plaintext} | ciphertext: {ciphertext} | runtime: Python"
        return helloworld_pb2.HelloReply(message=msg)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start AES-python server. Addr: " + address)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    # logging.basicConfig()
    serve()