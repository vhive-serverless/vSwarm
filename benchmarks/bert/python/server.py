import subprocess
import mlperf_loadgen as lg
import argparse
import os
import sys
import re
# protobuf
from proto.bert import bert_pb2
import bert_pb2_grpc
import grpc
from concurrent import futures
# from grpc_reflection.v1alpha import reflection

sys.path.insert(0, os.getcwd())


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend", choices=["tf", "pytorch", "onnxruntime", "tf_estimator"], default="pytorch", help="Backend")
    parser.add_argument("--scenario", choices=["SingleStream", "Offline",
                        "Server", "MultiStream"], default="Offline", help="Scenario")
    parser.add_argument("--accuracy", action="store_true",
                        help="enable accuracy pass")
    parser.add_argument("--quantized", action="store_true",
                        help="use quantized model (only valid for onnxruntime backend)")
    parser.add_argument("--profile", action="store_true",
                        help="enable profiling (only valid for onnxruntime backend)")
    parser.add_argument(
        "--mlperf_conf", default="build/mlperf.conf", help="mlperf rules config")
    parser.add_argument("--user_conf", default="user.conf",
                        help="user config for user LoadGen settings such as target QPS")
    parser.add_argument("--max_examples", type=int,
                        help="Maximum number of examples to consider (not limited by default)")
    parser.add_argument("-a", "--addr", dest="addr", default="0.0.0.0", help="IP address")
    parser.add_argument("-p", "--port", dest="port", default="50051", help="serve port")
    args = parser.parse_args()
    return args


scenario_map = {
    "SingleStream": lg.TestScenario.SingleStream,
    "Offline": lg.TestScenario.Offline,
    "Server": lg.TestScenario.Server,
    "MultiStream": lg.TestScenario.MultiStream
}


def do_bert_inference():
    args = get_args()

    if args.backend == "pytorch":
        assert not args.quantized, "Quantized model is only supported by onnxruntime backend!"
        assert not args.profile, "Profiling is only supported by onnxruntime backend!"
        from pytorch_SUT import get_pytorch_sut
        sut = get_pytorch_sut(args)
    elif args.backend == "tf":
        assert not args.quantized, "Quantized model is only supported by onnxruntime backend!"
        assert not args.profile, "Profiling is only supported by onnxruntime backend!"
        from tf_SUT import get_tf_sut
        sut = get_tf_sut(args)
    elif args.backend == "tf_estimator":
        assert not args.quantized, "Quantized model is only supported by onnxruntime backend!"
        assert not args.profile, "Profiling is only supported by onnxruntime backend!"
        from tf_estimator_SUT import get_tf_estimator_sut
        sut = get_tf_estimator_sut()
    elif args.backend == "onnxruntime":
        from onnxruntime_SUT import get_onnxruntime_sut
        sut = get_onnxruntime_sut(args)
    else:
        raise ValueError("Unknown backend: {:}".format(args.backend))

    settings = lg.TestSettings()
    settings.scenario = scenario_map[args.scenario]
    settings.FromConfig(args.mlperf_conf, "bert", args.scenario)
    settings.FromConfig(args.user_conf, "bert", args.scenario)

    if args.accuracy:
        settings.mode = lg.TestMode.AccuracyOnly
    else:
        settings.mode = lg.TestMode.PerformanceOnly
    log_path = os.environ.get("LOG_PATH")
    if not log_path:
        log_path = "build/logs"
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_output_settings = lg.LogOutputSettings()
    log_output_settings.outdir = log_path
    log_output_settings.copy_summary_to_stdout = True
    log_settings = lg.LogSettings()
    log_settings.log_output = log_output_settings
    log_settings.enable_trace = True

    print("Running LoadGen test...")
    lg.StartTestWithLogSettings(sut.sut, sut.qsl.qsl, settings, log_settings)
    if args.accuracy and not os.environ.get("SKIP_VERIFY_ACCURACY"):
        cmd = "python3 {:}/accuracy-squad.py {}".format(
            os.path.dirname(os.path.abspath(__file__)),
            '--max_examples {}'.format(
                args.max_examples) if args.max_examples else '')
        subprocess.check_call(cmd, shell=True)

    print("Done!")

    print("Destroying SUT...")
    lg.DestroySUT(sut.sut)

    print("Destroying QSL...")
    lg.DestroyQSL(sut.qsl.qsl)

    summary_file = "./build/logs/mlperf_log_summary.txt"
    while True:
        if not os.path.isfile(summary_file): continue
        if os.stat(summary_file).st_size == 0: continue
        latency_dict = parse_summary_file(summary_file)
        if latency_dict == None: continue
        
        return latency_dict

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


class Greeter(bert_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        token = request.name
        print("Start to do bert inference...")
        latency_dict = do_bert_inference()
        return bert_pb2.HelloReply(
            min_latency = latency_dict["Min latency (ns)"],
            max_latency = latency_dict["Max latency (ns)"],
            mean_latency = latency_dict["Mean latency (ns)"]
        )
        

def serve():
    args = get_args()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    bert_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    # SERVICE_NAMES = (
    #     bert_pb2.DESCRIPTOR.services_by_name['Greeter'].full_name,
    #     reflection.SERVICE_NAME,
    # )
    # reflection.enable_server_reflection(SERVICE_NAMES, server)

    address = (args.addr + ":" + args.port)
    server.add_insecure_port(address)
    print("Start Bert-python server. Addr: " + address)
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
    