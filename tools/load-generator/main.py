import os
import sys

import json
import argparse

from log_config import *
from load_generator.plot_stats import *
from load_generator.trace_parser import *
from load_generator.load_generator import *
from load_generator.find_proxy_function import *
from load_generator.deployer import *


def plot_stat(args):
    """
    This function plots the collected statistics and output PNG files
    """

    if (args.dbg == "True" or args.dbg == True): setLogLevel("DEBUG")
    else: setLogLevel("INFO") 

    trace_directorypath = args.trace
    profile_filepath = args.profile
    output_folder = args.png_folder

    # Load the trace functions from the mentioned directorypath
    trace_functions, err = load_trace(trace_directorypath)
    if err == -1:
        log.info(f"Loading trace failed")
        return
    elif err == 0:
        log.info(f"Trace loaded")

    # Collecting details associated with memory and duration of trace functions
    memory = []
    duration = []
    for function_name in trace_functions:
        memory.append(trace_functions[function_name]["memory"]["75-percentile"])
        duration.append(trace_functions[function_name]["duration"]["75-percentile"])

    # Obtain the proxy functions
    # Check whether the profile file for proxy functions exists or not
    if os.path.exists(profile_filepath):
        log.info(
            f"Profile file for proxy functions {profile_filepath} exists. Accessing information"
        )
        try:
            with open(profile_filepath, "r") as jf:
                proxy_functions = json.load(jf)
        except Exception as e:
            log.critical(
                f"Profile file for proxy functions {profile_filepath} cannot be read. Error: {e}"
            )
            return
    else:
        log.critical(f"Profile file for proxy functions {profile_filepath} not found")
        return

    # Collecting details associated with memory, cpu duration of proxy functions
    proxy_memory = []
    proxy_duration = []
    proxy_cpu = []
    for function_name in proxy_functions:
        proxy_memory.append(proxy_functions[function_name]["memory"]["75-percentile"])
        proxy_duration.append(
            proxy_functions[function_name]["duration"]["75-percentile"]
        )
        proxy_cpu.append(proxy_functions[function_name]["cpu"]["75-percentile"])

    # Check whether folder where PNG files are to be saved exists or not
    if not os.path.exists(output_folder):
        log.info(f"{output_folder} directory does not exist.")
        os.makedirs(output_folder)
        log.info(f"{output_folder} directory created")
    else:
        pass

    # Plotting utilization details of proxy functions
    plot_hist_log_scale(
        data=proxy_memory,
        data_name="memory utilization of proxy functions",
        plot_name="Memory Utilization Distribution of proxy functions",
        xlabel="Memory (Mb)",
        ylabel="Frequency",
        png_filename=f"{output_folder}/proxy-functions-memory-utilization.png",
    )
    plot_hist_log_scale(
        data=proxy_cpu,
        data_name="cpu utilization of proxy functions",
        plot_name="CPU Utilization Distribution of proxy functions",
        xlabel="CPU Utilization",
        ylabel="Frequency",
        png_filename=f"{output_folder}/proxy-functions-cpu-utilization.png",
    )
    plot_hist_log_scale(
        data=proxy_duration,
        data_name="Duration of proxy functions",
        plot_name="Duration Distribution of proxy functions",
        xlabel="Time Duration (milliseconds)",
        ylabel="Frequency",
        png_filename=f"{output_folder}/proxy-functions-duration.png",
    )

    # Plotting utilization details of trace functions
    plot_hist_log_scale_compare_data(
        data=memory,
        data_name="memory utilization of trace functions",
        compare_data=proxy_memory,
        scatterplot_label="memory utilization of proxy functions",
        plot_name="Memory Utilization Distribution of trace functions",
        xlabel="Memory (Mb)",
        ylabel="Frequency",
        png_filename=f"{output_folder}/trace-functions-memory-utilization.png",
    )
    plot_hist_log_scale_compare_data(
        data=duration,
        data_name="duration of trace functions",
        compare_data=proxy_duration,
        scatterplot_label="duration of proxy functions",
        plot_name="Duration Distribution of trace functions",
        xlabel="Time Duration (milliseconds)",
        ylabel="Frequency",
        png_filename=f"{output_folder}/trace-functions-duration-utilization.png",
    )

    # Scatter plot on log scale
    trace_points = []
    for i in range(len(memory)):
        trace_points.append((memory[i], duration[i]))
    proxy_points = []
    for i in range(len(proxy_memory)):
        proxy_points.append((proxy_memory[i], proxy_duration[i]))
    plot_scatter_logx_logy(
        data1=trace_points,
        data1_label="Trace Functions",
        data2=proxy_points,
        data2_label="Proxy Functions",
        plot_name="Function profiles",
        xlabel="Memory Utilization (Mb) (log scale)",
        ylabel="Duration (milliseconds) (log scale)",
        png_filename=f"{output_folder}/function-profiles.png",
    )


def generate_load(args):
    """
    This function generates the load
    """

    if (args.dbg == "True" or args.dbg == "true" or args.dbg == True): setLogLevel("DEBUG")
    else: setLogLevel("INFO") 

    load_output_filepath = args.output
    trace_directorypath = args.trace
    profile_filepath = args.profile
    config_proxy_filepath = args.config_proxy
    build_directorypath = args.build
    minute_granularity = (args.minute == "True") or (args.minute == True)  
    unique_assignment = (args.unique == "True") or (args.unique == True)
    iat_distribution = args.iat_distribution
    expt_duration = int(args.duration)
    warmup_duration = int(args.warmup_duration)
    duration = expt_duration + warmup_duration

    # Load the trace functions from the mentioned directorypath
    trace_functions, err = load_trace(trace_directorypath)
    if err == -1:
        log.critical(f"Load Generation failed")
        return
    elif err == 0:
        log.info(f"Trace loaded")

    # Check whether the profile file for proxy functions exists or not
    if os.path.exists(profile_filepath):
        log.info(
            f"Profile file for proxy functions {profile_filepath} exists. Accessing information"
        )
        try:
            with open(profile_filepath, "r") as jf:
                proxy_functions = json.load(jf)
        except Exception as e:
            log.critical(
                f"Profile file for proxy functions {profile_filepath} cannot be read. Error: {e}"
            )
            log.critical(f"Load Generation failed")
            return
    else:
        log.critical(f"Profile file for proxy functions {profile_filepath} not found")
        log.critical(f"Load Generation failed")
        return

    # Getting a proxy function for every trace function
    trace_functions, err = get_proxy_function(
        trace_functions=trace_functions,
        proxy_functions=proxy_functions,
        unique_assignment=unique_assignment,
    )
    if err == -1:
        log.critical(f"Load Generation failed")
        return
    elif err == 0:
        log.info(f"Proxy functions obtained")

    # Check if the shell path is bash
    err = check_shell_path()
    if err == -1:
        log.critical(f"Load Generation failed")
        return

    # Delete all the services
    delete_all_services()

    # Deploy proxy services
    trace_functions, proxy_functions, err = deploy_services(
        trace_functions=trace_functions,
        proxy_functions=proxy_functions,
        build_shell_scripts_location=build_directorypath,
        config_file=config_proxy_filepath,
    )
    if err == -1:
        log.critical(f"Load Generation failed")
        return
    elif err == 0:
        log.info(f"Proxy services deployed")

    # Collect the endpoints of the proxy functions
    trace_functions, err = collect_endpoints(trace_functions=trace_functions)
    if err == -1:
        log.critical(f"Load Generation failed")
        return
    elif err == 0:
        log.info(f"Endpoints for proxy services collected")

    # Generate the load
    trace_functions = get_invocation_timestamp(
        trace_functions=trace_functions,
        iat_distribution=iat_distribution,
        minute_granularity=minute_granularity,
    )
    load = generate_load_timestamp(trace_functions=trace_functions, duration=duration)
    try:
        with open(load_output_filepath, "w") as jf:
            json.dump(load, jf, indent=3)
        log.info(
            f"Load Generation completed and written into file {load_output_filepath}"
        )
    except Exception as e:
        log.critical(f"Load Generation failed. Error: {e}")

    return


def main():

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    plot_parser = subparser.add_parser("plot")

    plot_parser.add_argument(
        "-t",
        "--trace",
        metavar="path",
        required=False,
        default="full-trace",
        help="Directory in which durations, invocations, memory CSV files of trace are located",
    )

    plot_parser.add_argument(
        "-p",
        "--profile",
        metavar="path",
        required=False,
        default="profile.json",
        help="JSON file containing profile details of the proxy functions",
    )

    plot_parser.add_argument(
        "-o",
        "--png_folder",
        metavar="path",
        required=False,
        default="png",
        help="Output folder where plots are stored",
    )

    plot_parser.add_argument(
        "-dbg",
        "--dbg",
        metavar="bool",
        required=False,
        default=True,
        help="Show debug messages",
    )

    loadgen_parser = subparser.add_parser("loadgen")

    loadgen_parser.add_argument(
        "-o",
        "--output",
        metavar="path",
        required=False,
        default="invoker/load.json",
        help="Output JSON file containing timestamps and endpoints of load",
    )

    loadgen_parser.add_argument(
        "-t",
        "--trace",
        metavar="path",
        required=False,
        default="trace",
        help="Directory in which durations, invocations, memory CSV files of trace are located",
    )

    loadgen_parser.add_argument(
        "-p",
        "--profile",
        metavar="path",
        required=False,
        default="profile.json",
        help="JSON file containing profile details of the proxy functions",
    )

    loadgen_parser.add_argument(
        "-c",
        "--config_proxy",
        metavar="path",
        required=False,
        default="config.json",
        help="Contains details about proxy functions used for deploying",
    )

    loadgen_parser.add_argument(
        "-b",
        "--build",
        metavar="path",
        required=False,
        default="build",
        help="Directory in which temporary build files are located",
    )

    loadgen_parser.add_argument(
        "-m",
        "--minute",
        metavar="bool",
        required=False,
        default=True,
        help="Trace contains information at minute/second granularity. True if minute granularity",
    )

    loadgen_parser.add_argument(
        "-u",
        "--unique",
        metavar="bool",
        required=False,
        default=False,
        help="Proxy-Trace functions mapping. Should it be unique?",
    )

    loadgen_parser.add_argument(
        "-i",
        "--iat_distribution",
        metavar="string",
        required=False,
        default="uniform",
        help="IAT Distribution: equidistant, unique or exponential",
    )

    loadgen_parser.add_argument(
        "-d",
        "--duration",
        metavar="int",
        required=False,
        default=20,
        help="Experiment Duration",
    )

    loadgen_parser.add_argument(
        "-w",
        "--warmup_duration",
        metavar="int",
        required=False,
        default=2,
        help="Warmup Duration",
    )

    loadgen_parser.add_argument(
        "-dbg",
        "--dbg",
        metavar="bool",
        required=False,
        default=True,
        help="Show debug messages",
    )

    args = parser.parse_args()

    if args.cmd == "plot":
        plot_stat(args)

    elif args.cmd == "loadgen":
        generate_load(args)


if __name__ == "__main__":
    sys.exit(main())
