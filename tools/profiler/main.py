import os
import sys

import json
import glob
import threading

from log_config import *
import argparse

from profiler.deployer import *
from profiler.profiler import *
from profiler.plot_stats import *


def run_and_collect_stats(args):
    """
    This function deploys the services, collects the statistics and outputs in JSON format
    """

    if (args.dbg == "True" or args.dbg == "true" or args.dbg == True): setLogLevel("DEBUG")
    else: setLogLevel("INFO") 

    metrics_server_loc = args.metrics_server
    yamls_folder = args.yaml_files
    build_folder = args.build
    config_file = args.config_file
    output_file = args.output_json

    rps = float(args.rps)
    iterations = int(args.sample_iter)
    run_duration = float(args.run_duration)
    sample_time_period = run_duration / iterations

    # Check whether shell path is bash
    err = check_shell_path()
    if err != 0:
        log.critical(f"Statistics collection failed")
        return

    # Check whether Metrics Server is deployed or not
    run_metrics = False
    if os.path.exists(metrics_server_loc):
        err = deploy_metrics_server(metrics_server_loc)
        if err != 0:
            log.critical(
                f"Metrics Server YAML file not found. CPU and Memory metrics are not obtained"
            )
        else:
            run_metrics = True
    else:
        log.critical(
            f"Metrics Server YAML file not found. CPU and Memory metrics are not obtained"
        )

    # If config file is available, then obtain the YAML filename, corresponding
    # predeployment and postdeployment commands from the config file.
    # If config file is not available, or read improperly, then deploy all the YAML
    # files in the yamls_folder with default commands.
    utilize_config_file = False
    functions = []

    # Check whether the config file exists or not
    # If exists, then obtain information from that
    if os.path.exists(config_file):
        log.info(f"Config file {config_file} exists. Accessing information")
        try:
            with open(config_file, "r") as jf:
                data = json.load(jf)
            for function_dict in data:
                function = {}
                try:
                    function["yaml-location"] = function_dict["yaml-location"]
                except:
                    continue
                try:
                    function["predeployment-commands"] = function_dict[
                        "predeployment-commands"
                    ]
                except:
                    function["predeployment-commands"] = []
                try:
                    function["postdeployment-commands"] = function_dict[
                        "postdeployment-commands"
                    ]
                except:
                    function["postdeployment-commands"] = []
                functions.append(function)
            utilize_config_file = True
        except Exception as e:
            log.warning(f"Config file {config_file} cannot be read")
    else:
        log.warning(f"Config file {config_file} cannot be read")

    if not utilize_config_file:
        log.warning(
            f"Config file {config_file} error. All the YAML files in {yamls_folder} are profiled"
        )
        search_pattern = os.path.join(yamls_folder, "*.yaml")
        yaml_files = glob.glob(search_pattern)
        for yf in yaml_files:
            function = {}
            function["yaml-location"] = yf
            function["predeployment-commands"] = []
            function["postdeployment-commands"] = []
            functions.append(function)

    stats = {}

    # Collect stats for all the functions
    for f in functions:

        # Delete all services
        delete_all_services()

        # The folder within build directory where build and data files will be stored
        yaml_name = os.path.basename(f["yaml-location"]).replace(".yaml", "")

        # Deploy the service
        function_name, err = deploy_service(
            yaml_filename=f["yaml-location"],
            predeployment_commands=f["predeployment-commands"],
            postdeployment_commands=f["postdeployment-commands"],
            build_shell_scripts_location=f"{build_folder}/{yaml_name}",
        )
        if err != 0:
            continue
        else:
            stats[f"{function_name}"] = {}
            stats[f"{function_name}"]["name"] = function_name
            stats[f"{function_name}"]["yaml"] = f["yaml-location"]

        # Collect the endpoint
        _, err = get_endpoint(
            function_name=function_name,
            endpoint_file_location=f"{build_folder}/{yaml_name}",
        )
        if err != 0:
            continue

        # Run invoker in the background
        run_invoker_in_background = threading.Thread(
            target=run_invoker,
            args=(
                "invoker",
                f"{build_folder}/{yaml_name}",
                f"{build_folder}/{yaml_name}",
                f"{build_folder}/{yaml_name}",
                rps,
                run_duration,
            ),
        )
        run_invoker_in_background.start()

        # Start collecting data from metrics server
        if run_metrics:
            pod_name, _, _, _ = get_metrics_server_data(
                function_name=function_name,
                run_duration=run_duration,
                sample_time_period=sample_time_period,
                memory_txt_location=f"{build_folder}/{yaml_name}",
                cpu_txt_location=f"{build_folder}/{yaml_name}",
            )

        # Join the invoker
        run_invoker_in_background.join()

        # collect the stats
        data, _ = collect_stats(
            function_name=function_name,
            duration_txt_location=f"{build_folder}/{yaml_name}",
            memory_txt_location=f"{build_folder}/{yaml_name}",
            cpu_txt_location=f"{build_folder}/{yaml_name}",
        )
        stats[f"{function_name}"]["cpu"] = data["cpu"]
        stats[f"{function_name}"]["memory"] = data["memory"]
        stats[f"{function_name}"]["duration"] = data["duration"]

        if pod_name != None:
            _ = delete_pod(pod_name=pod_name)
            _ = wait_until_pod_is_deleted(pod_name=pod_name)

        # Delete all services
        delete_all_services()

    with open(output_file, "w") as json_file:
        json.dump(stats, json_file, indent=4)

    log.info(f"Function profiles written to {output_file} JSON file")


def plot_stat(args):
    """
    This function plots the collected statistics and output PNG files
    """

    input_stats = args.stat_file
    output_folder = args.png_folder

    memory = []
    cpu = []
    duration = []

    # Check whether the stat file exists or not
    # If exists, then obtain information from that
    if os.path.exists(input_stats):
        log.info(f"Stat file {input_stats} exists. Accessing information")
        try:
            with open(input_stats, "r") as jf:
                stats = json.load(jf)
            for function in stats.values():
                memory.append(function["memory"]["75-percentile"])
                cpu.append(function["cpu"]["75-percentile"])
                duration.append(function["duration"]["75-percentile"])
        except Exception as e:
            log.critical(f"Stat file {input_stats} cannot be read. Error: {e}")
            return
    else:
        log.critical(f"Stat file {input_stats} not found")
        return

    # Write the output pngs to the request folder 
    # Check whether folder exists or not
    if not os.path.exists(output_folder):
        log.info(f"{output_folder} directory does not exist.")
        os.makedirs(output_folder)
        log.info(f"{output_folder} directory created")
    else:
        pass

    plot_histograms(memory=memory, duration=duration, cpu=cpu, output_folder=output_folder)





def main():

    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="cmd")

    collect_parser = subparser.add_parser("profile")

    collect_parser.add_argument(
        "-dbg",
        "--dbg",
        metavar="bool",
        required=False,
        default=False,
        help="Set logger level to debug",
    )
    collect_parser.add_argument(
        "-metset",
        "--metrics_server",
        metavar="path",
        required=False,
        default="metrics-server/components.yaml",
        help="Path to Metrics Server YAML deployment file",
    )
    collect_parser.add_argument(
        "-yaml",
        "--yaml_files",
        metavar="path",
        required=False,
        default="yamls",
        help="Path to Function YAML files",
    )
    collect_parser.add_argument(
        "-build",
        "--build",
        metavar="path",
        required=False,
        default="build",
        help="Path to build files. Temporary location to build",
    )
    collect_parser.add_argument(
        "-config",
        "--config_file",
        metavar="path",
        required=False,
        default="config.json",
        help="Config file location",
    )
    collect_parser.add_argument(
        "-o",
        "--output_json",
        metavar="path",
        required=False,
        default="profile.json",
        help="Output file location",
    )

    collect_parser.add_argument(
        "-rps",
        "--rps",
        metavar="float",
        type=float,
        required=False,
        default=0.2,
        help="RPS at which functions must be invoked",
    )
    collect_parser.add_argument(
        "-iter",
        "--sample_iter",
        metavar="integer",
        type=int,
        required=False,
        default=5,
        help="Number of sample iterations",
    )
    collect_parser.add_argument(
        "-dur",
        "--run_duration",
        metavar="float",
        type=float,
        required=False,
        default=50 * 2,
        help="Run Duration",
    )


    plot_parser = subparser.add_parser("plot")
    
    plot_parser.add_argument(
        "-i",
        "--stat_file",
        metavar="path",
        required=False,
        default="output.json",
        help="JSON file where profile details are stored",
    )

    plot_parser.add_argument(
        "-o",
        "--png_folder",
        metavar="path",
        required=False,
        default="png/",
        help="Output folder where plots are stored",
    )


    args = parser.parse_args()

    if args.cmd == "profile":
        run_and_collect_stats(args)

    elif args.cmd == "plot":
        plot_stat(args)


if __name__ == "__main__":
    sys.exit(main())
