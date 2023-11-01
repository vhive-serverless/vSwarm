import os
from backend import get_SUT
import argparse
import mlperf_loadgen as lg

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--backend", choices=["pytorch"], default="pytorch", help="Backend")
    parser.add_argument("--scenario", choices=["SingleStream", "Offline",
                        "Server"], default="Offline", help="Scenario")
    parser.add_argument("--model-path", default="EleutherAI/gpt-j-6b", help="")
    parser.add_argument(
        "--dataset-path", default="./data/cnn_eval.json", help="")
    parser.add_argument("--accuracy", action="store_true",
                        help="enable accuracy pass")
    parser.add_argument("--dtype", default="float32", help="data type of the model, choose from float16, bfloat16 and float32")
    parser.add_argument("--quantized", action="store_true",
                        help="use quantized model (only valid for onnxruntime backend)")
    parser.add_argument("--profile", action="store_true",
                        help="enable profiling (only valid for onnxruntime backend)")
    parser.add_argument("--gpu", action="store_true",
                        help="use GPU instead of CPU for the inference")
    parser.add_argument("--audit_conf", default="audit.conf",
                        help="audit config for LoadGen settings during compliance runs")
    parser.add_argument(
        "--mlperf_conf", default="mlperf.conf", help="mlperf rules config")
    parser.add_argument("--user_conf", default="user.conf",
                        help="user config for user LoadGen settings such as target QPS")
    parser.add_argument("--max_examples", type=int, default=1,
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


def do_gpt_inference():
    args = get_args()
    print(args)

    sut = get_SUT(
        model_path=args.model_path,
        scenario=args.scenario,
        dtype=args.dtype,
        dataset_path=args.dataset_path,
        max_examples=args.max_examples,
        use_gpu=args.gpu,
    )

    settings = lg.TestSettings()
    settings.scenario = scenario_map[args.scenario]
    # Need to update the conf
    settings.FromConfig(args.mlperf_conf, "gptj", args.scenario)
    settings.FromConfig(args.user_conf, "gptj", args.scenario)

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

    lg.StartTestWithLogSettings(sut.sut, sut.qsl, settings, log_settings, args.audit_conf)
    print("Test Done!")

    print("Destroying SUT...")
    lg.DestroySUT(sut.sut)

    print("Destroying QSL...")
    lg.DestroyQSL(sut.qsl)


if __name__ == '__main__':
    do_gpt_inference()