from concurrent import futures
import logging

import grpc

import random
import string

# adding python tracing sources to the system path
sys.path.insert(0, os.getcwd() + '/../../../../utils/tracing/python')
import tracing

import os
import sys

# sys.path.append('../proto')  # for local testing (i.e. not running in Docker-compose)
import helloworld_pb2
import helloworld_pb2_grpc

import ctypes
libc = ctypes.CDLL(None)
syscall = libc.syscall

print("python version: %s" % sys.version)
print("Server has PID: %d" % os.getpid())
GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")

if tracing.IsTracingEnabled():
    tracing.initTracer("auth", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()

class Empty:  # declare this class to enable dynamically adding new attributes
    pass

def generatePolicy(principalId, effect, resource):
    authResponse = Empty()

    authResponse.principalId = principalId
    if effect and resource:
        policyDocument = Empty()
        policyDocument.Version = '2012-10-17'
        policyDocument.Statement = [None]
        statementOne = Empty()
        statementOne.Action = 'execute-api:Invoke'
        statementOne.Effect = effect
        statementOne.Resource = resource
        policyDocument.Statement[0] = statementOne
        authResponse.policyDocument = policyDocument
    
    # Optional output with custom properties of the String, Number or Boolean type.
    authResponse.context = {
      "stringKey": "stringval",
      "numberKey": 123,
      "booleanKey": True
    }

    return authResponse




class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):

        token = request.name
        fakeMethodArn = "arn:aws:execute-api:{regionId}:{accountId}:{apiId}/{stage}/{httpVerb}/[{resource}/[{child-resources}]]"
        
        with tracing.Span("Generate Policy"):
            if '.f2' in token:
                generatePolicy('user', 'Allow', fakeMethodArn)
                msg = 'auth.f2'
            else:
                generatePolicy('user', 'Deny', fakeMethodArn)
                msg = 'auth.f1'

            gid = syscall(104)
            msg = "Serve Function: Python.%s: from GID: %i" % (msg, gid)
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
