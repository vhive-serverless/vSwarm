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

import os
import sys

import tracing

import pyaes

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']

if not LAMBDA:
    import grpc
    import argparse

    from proto.aes import aes_pb2
    import aes_pb2_grpc

    from concurrent import futures

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
    parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
    parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
    parser.add_argument("-k", "--key", dest="KEY", default="6368616e676520746869732070617373", help="Secret key")
    parser.add_argument("--default_plaintext", default="defaultplaintext", help="Default plain text if plaintext_message is empty or 'world'")
    args = parser.parse_args()

    KEY = args.KEY.encode(encoding = 'UTF-8')

if LAMBDA:
    inputKey = os.environ.get('AES_KEY', '6368616e676520746869732070617373')
    KEY = inputKey.encode(encoding = 'UTF-8')

if tracing.IsTracingEnabled():
    tracing.initTracer("aes-python", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()


def AESModeCTR(plaintext):
    counter = pyaes.Counter(initial_value = 0)
    aes = pyaes.AESModeOfOperationCTR(KEY, counter = counter)
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

if not LAMBDA:
    class Aes(aes_pb2_grpc.AesServicer):
        def ShowEncryption(self, request, context):
            if request.plaintext_message in ["", "world"]:
                plaintext = args.default_plaintext
            else:
                plaintext = request.plaintext_message
            with tracing.Span("AES Encryption"):
                ciphertext = AESModeCTR(plaintext)
            msg = f"fn: AES | plaintext: {plaintext} | ciphertext: {ciphertext} | runtime: Python"
            return aes_pb2.ReturnEncryptionInfo(encryption_info=msg)

if LAMBDA:
    class Aes():
        def Encrypt(self, plaintext):
            ciphertext = AESModeCTR(plaintext)
            msg = f"fn: AES | plaintext: {plaintext} | ciphertext: {ciphertext} | runtime: Python"
            return msg

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    aes_pb2_grpc.add_AesServicer_to_server(Aes(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start AES-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

def lambda_handler(event, context):
    aesObj = Aes()
    return aesObj.Encrypt(event['plaintext'])

if __name__ == '__main__':
    serve()
