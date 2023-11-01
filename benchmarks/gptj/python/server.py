#  MIT License

#  Copyright (c) 2022 EASE lab

#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:

#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.

#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

from concurrent import futures
import os
import sys
from backend import get_SUT
import grpc
import logging
import argparse
import mlperf_loadgen as lg
import re

from gptj_pb2_grpc import GptJBenchmarkServicer, add_GptJBenchmarkServicer_to_server
from grpc_reflection.v1alpha import reflection
import gptj_pb2
from gptj_pb2 import GptJBenchmarkReply
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
            print(e)
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
    summary_file = "./python/build/logs/mlperf_log_summary.txt"
    invalid = {
        "Min latency (ns)": -1,
        "Max latency (ns)": -1,
        "Mean latency (ns)": -1,
    }
    if not os.path.isfile(summary_file): 
        return invalid
    if os.stat(summary_file).st_size == 0:
        return invalid
    latency_dict = parse_summary_file(summary_file)
    if latency_dict == None:
        return invalid
    
    return latency_dict
    
    
class GptJBenchmarkServicer(GptJBenchmarkServicer):
    def GetBenchmark(self, request, context):
        if (request.regenerate == "true"):
            do_gpt_inference()

        logging.info("Read gpt-j summary file...")
        latency_dict = read_summary_file()
        logging.info("Read gpt-j summary file done")
        logging.info(latency_dict)
        return GptJBenchmarkReply(
            latency_info = f"Min latency (ns): {latency_dict['Min latency (ns)']} | Max latency (ns): {latency_dict['Max latency (ns)']} | Mean latency (ns): {latency_dict['Mean latency (ns)']}"
        )

def serve():
    args = get_args()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
    add_GptJBenchmarkServicer_to_server(GptJBenchmarkServicer(), server)
    
    SERVICE_NAMES = (
        gptj_pb2.DESCRIPTOR.services_by_name['GptJBenchmark'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address) 
    logging.info("Start server: listen on : " + address)
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    serve()