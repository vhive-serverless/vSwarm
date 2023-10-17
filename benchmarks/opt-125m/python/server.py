from concurrent import futures
import os
import sys
from backend import get_SUT
import grpc
import logging
import argparse
import mlperf_loadgen as lg
import re

from opt_125m_pb2_grpc import Opt125mBenchmarkServicer, add_Opt125mBenchmarkServicer_to_server
from opt_125m_pb2 import Opt125mBenchmarkReply
from main_process import do_gpt_inference, get_args


print("python version: %s" % sys.version)
print("Server has PID: %d" % os.getpid())
GRPC_PORT_ADDRESS = os.getenv("GRPC_PORT")


def parse_summary_file(summary_file):
    keys = ["Min latency (ns)", "Max latency (ns)", "Mean latency (ns)"]
    res_dic = {}
    with open(summary_file) as f:
        try:
            text = f.read()
            for key in keys:
                val = extract_text_between_strings(text,key,"\n")

                res_dic[key] = int(val.split(': ')[-1])
        except Exception as e:
            # print(e)
            return None
    return res_dic
        

def extract_text_between_strings(text, str1, str2):
    try:
        pattern = re.escape(str1) + r'(.*?)' + re.escape(str2)
        match = re.search(pattern, text, re.DOTALL)
        if match:
            extracted_text = match.group(1)
            return extracted_text
        else:
            raise Exception('Pattern not found in the text for start: %s'%(str1))
    except IOError:
        raise Exception('Failed to read the file')
    
def read_summary_file():
    summary_file = "./build/logs/mlperf_log_summary.txt"
    while True:
        if not os.path.isfile(summary_file): continue
        if os.stat(summary_file).st_size == 0: continue
        latency_dict = parse_summary_file(summary_file)
        if latency_dict == None: continue
        
        return latency_dict
    
    
class Opt125mBenchmarkServicer(Opt125mBenchmarkServicer):
    def GetBenchmark(self, request, context):
        if (request.regenerate):
            do_gpt_inference()

        print("Read gpt-j summary file...")
        latency_dict = read_summary_file()
        return Opt125mBenchmarkReply(
            min_latency = latency_dict["Min latency (ns)"],
            max_latency = latency_dict["Max latency (ns)"],
            mean_latency = latency_dict["Mean latency (ns)"]
        )


def serve():
    args = get_args()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    add_Opt125mBenchmarkServicer_to_server(Opt125mBenchmarkServicer(), server)
    

    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address) 
    logging.info("Start server: listen on : " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()