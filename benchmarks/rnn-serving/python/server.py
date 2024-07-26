import os
import sys

import pickle
import numpy as np
import torch
import rnn
import string
import random

import tracing

import grpc
import argparse

from proto.rnn_serving import rnn_serving_pb2
import rnn_serving_pb2_grpc

from concurrent import futures 

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
parser.add_argument("-zipkin", "--zipkin", dest="url", default="http://0.0.0.0:9411/api/v2/spans", help="Zipkin endpoint url")
parser.add_argument("--default_language", default="French", help="Default Language in which string will be generated")
parser.add_argument("--num_strings", default=3, help="Number of strings to be generated")

args = parser.parse_args()
args.num_strings = int(args.num_strings)

torch.set_num_threads(1)

rnn_model_path = "model/rnn_model.pth"

all_categories =['French', 'Czech', 'Dutch', 'Polish', 'Scottish', 'Chinese', 'English', 'Italian', 'Portuguese', 'Japanese', 'German', 'Russian', 'Korean', 'Arabic', 'Greek', 'Vietnamese', 'Spanish', 'Irish']
n_categories = len(all_categories)
all_letters = string.ascii_letters + " .,;'-"
n_letters = len(all_letters) + 1 

rnn_model = rnn.RNN(n_letters, 128, n_letters, all_categories, n_categories, all_letters, n_letters)
rnn_model.load_state_dict(torch.load(rnn_model_path))
rnn_model.eval()

all_start_letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

if tracing.IsTracingEnabled():
    tracing.initTracer("rnn-serving-python", url=args.url)
    tracing.grpcInstrumentClient()
    tracing.grpcInstrumentServer()

def GenerateStringThroughRNN(language, num_strings):
    try:
        start_letters = "".join(random.choices(all_start_letters, k=num_strings))
        output_names = list(rnn_model.samples(language, start_letters))
        return f"fn: RNN-Serving | language:{language}.n:{num_strings} | output:{output_names} | runtime: Python"
    except Exception as e:
        return f"fn: RNN-Serving | language:{language}.n:{num_strings} | RNNServingFailed.Error:{e} | runtime: Python"

class RNNServing(rnn_serving_pb2_grpc.RNNServingServicer):
    def GenerateString(self, request, context):
            
        if request.language not in all_categories:
            language = args.default_language
        else:
            language = request.language
            
        if request.numSamples <= 0:
            num_strings = args.num_strings
        else:
            num_strings = request.numSamples

        msg = GenerateStringThroughRNN(language, num_strings)
        return rnn_serving_pb2.GetString(message=msg)
                
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    rnn_serving_pb2_grpc.add_RNNServingServicer_to_server(RNNServing(), server)
    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start RNNServing-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()