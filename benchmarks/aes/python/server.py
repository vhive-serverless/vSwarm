from concurrent import futures
import logging

import grpc

import random
import string
import pyaes

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
    tracing.initTracer("aes", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()


def generate(length):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

KEY = b'\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,'
message = generate(100)
message2 = generate(100)

responses = ["record_response", "replay_response"]



def function1():
    plaintext = "exampleplaintext"
    aes = pyaes.AESModeOfOperationCTR(KEY)
    ciphertext = aes.encrypt(plaintext)
    return "Python.aes.f1", plaintext, ciphertext

def function2():
    plaintext = "a m e s s a g e "
    aes = pyaes.AESModeOfOperationCTR(KEY)
    ciphertext = aes.encrypt(plaintext)
    return "Python.aes.f2", plaintext, ciphertext

def function(plaintext):
    aes = pyaes.AESModeOfOperationCTR(KEY)
    ciphertext = aes.encrypt(plaintext)
    return "python.aes.fn", plaintext, ciphertext


class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):

        with tracing.Span("Plaintext selection and Encryption"):
            if request.name == "" or ".f1" in request.name:
                msg, plaintext, ciphertext = function1()
            elif ".f2" in request.name:
                msg, plaintext, ciphertext = function1()
            else:
                msg, plaintext, ciphertext = function(request.name)

        gid = syscall(104)
        msg = f"Hello: this is: {gid}. Invoke {msg} | Plaintext: {plaintext} Ciphertext: {ciphertext}"
        return helloworld_pb2.HelloReply(message=msg)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    helloworld_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)

    address = ('[::]:' + GRPC_PORT_ADDRESS if GRPC_PORT_ADDRESS else  '[::]:50051')
    server.add_insecure_port(address)
    print("Start server: listen on : " + address)

    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
