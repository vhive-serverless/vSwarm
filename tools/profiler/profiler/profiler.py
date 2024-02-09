import os
import subprocess

import json
import time
import numpy as np

from log_config import *
from typing import Tuple


def run_invoker(
    invoker_location: str,
    endpoints_location: str,
    duration_txt_location: str,
    invoker_output_location: str,
    rps: float,
    run_duration: float,
) -> int:
    """
    Runs the invoker. Functions are invoked

    Parameters:
    - `invoker_location` (str): invoker binary executable location
    - `endpoints_location` (str): endpoints.json file location
    - `duration_txt_location` (str): location at which latencies must be stored
    - `invoker_output_location` (str): invoker output stored in this location
    - `rps` (float): RPS
    - `run_duration` (float): Total time in seconds for which the invoker must be run

    Returns:
    - int: 0: No Error. -1: Error
    """

    try:
        log.debug(f"Function invocation started")
        run_invoker_command = f"sudo {invoker_location}/invoker -port=80 -time={int(run_duration)} -rps={rps} -dbg=true -endpointsFile='{endpoints_location}/endpoints.json' -latf='{duration_txt_location}/duration.txt' > {invoker_output_location}/invoker.log"
        result = subprocess.run(
            run_invoker_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.debug(f"Invoker execution completed with return code: {result.returncode}")
    except subprocess.CalledProcessError as e:
        log.error(
            f"Invoker execution failed Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
        )
        return -1
    except Exception as e:
        log.error(f"Invoker execution failed. Error: {e}")
        return -1
    log.debug(f"Function invocation successfully executed")
    return 0


def get_metrics_server_data(
    function_name: str,
    run_duration: float,
    sample_time_period: float,
    memory_txt_location: str,
    cpu_txt_location: str,
) -> Tuple[str, list, list, int]:
    """
    Obtains the pod name for the given function. Runs metrics-pod command to collect
    CPU and memory utilization data for the pod.

    Parameters:
    - `function_name` (str): function name
    - `run_duration` (float): Total time in seconds for which the measurements have to be made
    - `sample_time_period` (float): time period between iterations
    - `memory_txt_location` (str): location at which memory utilization details must be stored
    - `cpu_txt_location` (str): location at which cpu utilization details must be stored

    Returns:
    - `pod_name` (str): pod name of the function
    - `cpu` (list): list of cpu utilization details
    - `memory` (list): list of memory utilization details
    - `int`: 0: No Error. -1: Error
    """

    # Get the pod name for the given function name
    def get_pod_name(function_name: str) -> Tuple[str, int]:
        get_podlist_command = f"kubectl get pods -o=json"
        try:
            result = subprocess.run(
                get_podlist_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pods = json.loads(result.stdout)["items"]
            matching_pods = []
            for pod_info in pods:
                try:
                    pod_name = pod_info["metadata"]["name"]
                    if function_name in pod_info["metadata"]["labels"]["app"]:
                        matching_pods.append(pod_name)
                except Exception as e:
                    continue
            return matching_pods, 0
        except subprocess.CalledProcessError as e:
            log.warning(
                f"Function: {function_name}: Pod name can't be obtained. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
            )
            return None, -1
        except Exception as e:
            log.warning(
                f"Function: {function_name}: Pod name can't be obtained. Error: {e}"
            )
            return None, -1

    # Check whether the pod is running or not.
    def check_pod_status(pod_name: str) -> bool:
        get_podlist_command = f"kubectl get pods --no-headers"
        try:
            result = subprocess.run(
                get_podlist_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pods = result.stdout.decode("utf-8").strip().split("\n")
            for p in pods:
                if (pod_name == p.split()[0]) and (p.split()[2] == "Running"):
                    return True
            return False
        except subprocess.CalledProcessError as e:
            log.warning(
                f"Pod: {pod_name} status can't be obtained. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
            )
            return False
        except Exception as e:
            log.warning(f"Pod: {pod_name} status can't be obtained. Error: {e}")
            return False

    # Given the pod name, find the CPU and memory utilization of the pod
    def _get_metrics_server_data(pod_name: str) -> Tuple[str, str, int]:
        get_stat_command = f"kubectl top pod {pod_name} --no-headers"
        try:
            result = subprocess.run(
                get_stat_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pods = result.stdout.decode("utf-8").strip().split("\n")
            for p in pods:
                if pod_name in p:
                    cpu = p.split()[1]
                    memory = p.split()[2]
                    return cpu, memory, 0
            return None, None, -1
        except subprocess.CalledProcessError as e:
            log.warning(
                f"Metrics Server. kubectl top command failed. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
            )
            return None, None, -1
        except Exception as e:
            log.warning(f"Metrics Server. kubectl top command failed. Error: {e}")
            return None, None, -1

    # Monitor the pod list, until pod name is obtained
    # Monitoring happens every 2 seconds for 15 minutes. If it shows failure even after that then it returns failure
    monitor_time = 15 * 60
    sleep_time = 2
    status = False
    found_running_pod = None
    for _ in range(int(monitor_time / sleep_time)):
        time.sleep(sleep_time)
        matching_pods, err = get_pod_name(function_name)
        if err != 0 and len(matching_pods) != 0:
            continue
        for pod_name in matching_pods:
            pod_status = check_pod_status(pod_name)
            if pod_status: 
                found_running_pod = pod_name
                break
        if found_running_pod != None:
            status = True
            break
        else:
            continue

    if status:
        log.info(f"Pod: {found_running_pod}")
    else:
        log.error(f"Function {function_name}. Pod NOT Running")
        return None, [], [], -1

    # Sleep for 10 seconds. metrics-server is refreshed once every 15 seconds.
    # Hence the pod details may or may not reflect in the metrics server
    time.sleep(10)

    cpu = []  # Store CPU usage details over samples
    memory = []  # Store memory usage details over samples

    # Get the CPU and memory usage details and store it in a list
    for _ in range(int(run_duration / sample_time_period)):
        c, m, err = _get_metrics_server_data(pod_name)
        if err != -1:
            cpu.append(c)
            memory.append(m)
        time.sleep(sample_time_period)

    # Write the memory utilization data to memory.txt
    # Check whether folder where the memory.txt are to be located exists or not
    if not os.path.exists(memory_txt_location):
        log.debug(f"{memory_txt_location} directory does not exist.")
        os.makedirs(memory_txt_location)
        log.debug(f"{memory_txt_location} directory created")
    else:
        pass
    with open(f"{memory_txt_location}/memory.txt", "w") as f:
        for m in memory:
            f.write(str(m) + "\n")

    # Write the cpu utilization data to cpu.txt
    # Check whether folder where the cpu.txt are to be located exists or not
    if not os.path.exists(cpu_txt_location):
        log.debug(f"{cpu_txt_location} directory does not exist.")
        os.makedirs(cpu_txt_location)
        log.debug(f"{cpu_txt_location} directory created")
    else:
        pass
    with open(f"{cpu_txt_location}/cpu.txt", "w") as f:
        for c in cpu:
            f.write(str(c) + "\n")

    log.debug(
        f"{function_name}: {pod_name}: CPU & Memory utilization details written in {memory_txt_location}/memory.txt and  {cpu_txt_location}/cpu.txt"
    )
    return pod_name, cpu, memory, 0


# Do a stastical analysis on the collected data and get the percentile averages
def collect_stats(
    function_name: str,
    duration_txt_location: str,
    memory_txt_location: str,
    cpu_txt_location: str,
) -> Tuple[dict, int]:
    """
    Analyzes the collected data to generate percentile averages

    Parameters:
    - `function_name` (str): function name
    - `memory_txt_location` (str): location at which memory utilization details are stored
    - `cpu_txt_location` (str): location at which cpu utilization details are stored
    - `duration_txt_location` (str): location at which duration details are stored

    Returns:
    - `dict`: Dictionary with percentile averages of duration, cpu and memory
    - `int`: 0: No Error. -1: Error
    """

    # Given a list of numbers and the percentiles to be found, it returns the percentile averages
    def get_average_percentile(numbers: list, percentile_list: list):
        numbers.sort()
        average = []
        for i in range(len(numbers)):
            sub_array = numbers[: i + 1]
            average.append(sum(sub_array) / len(sub_array))
        percentiles = np.percentile(average, percentile_list)
        return percentiles

    def duration_stats(
        duration_txt_location: str, percentile_list: list
    ) -> Tuple[list, int]:
        try:
            with open(f"{duration_txt_location}/duration.txt", "r") as f:
                duration = [float(line.strip())/1000 for line in f] # By 1000 to convert to milliseocnds
                duration_percentiles = get_average_percentile(duration, percentile_list)
                return duration_percentiles, 0
        except FileNotFoundError:
            log.warning(f"{duration_txt_location}/duration.txt File not found")
            return [], -1
        except Exception as e:
            log.warning(f"{duration_txt_location}/duration.txt File. Error: {e}")
            return [], -1

    def memory_stats(
        memory_txt_location: str, percentile_list: list
    ) -> Tuple[list, int]:
        try:
            with open(f"{memory_txt_location}/memory.txt", "r") as f:
                memory = [float(line.strip()[:-2]) for line in f]
                memory_percentiles = get_average_percentile(memory, percentile_list)
                return memory_percentiles, 0
        except FileNotFoundError:
            log.warning(f"{memory_txt_location}/memory.txt File not found")
            return [], -1
        except Exception as e:
            log.warning(f"{memory_txt_location}/memory.txt File. Error: {e}")
            return [], -1

    def cpu_stats(cpu_txt_location: str, percentile_list: list) -> Tuple[list, int]:
        try:
            with open(f"{cpu_txt_location}/cpu.txt", "r") as f:
                cpu = [float(line.strip()[:-1]) for line in f]
                cpu_percentiles = get_average_percentile(cpu, percentile_list)
                return cpu_percentiles, 0
        except FileNotFoundError:
            log.warning(f"{cpu_txt_location}/cpu.txt File not found")
            return [], -1
        except Exception as e:
            log.warning(f"{cpu_txt_location}/cpu.txt File. Error: {e}")
            return [], -1

    function = {}
    function["cpu"] = {}
    function["memory"] = {}
    function["duration"] = {}

    percentile_list = [0, 1, 5, 25, 50, 75, 95, 99, 100]
    e = 0

    memory_percentiles, err = memory_stats(memory_txt_location, percentile_list)
    if err != 0:
        log.warning(f"Function {function_name} memory stats not collected")
        e = -1
    else:
        log.debug(f"Function {function_name} memory stats collected")
        for p in percentile_list:
            function["memory"][f"{p}-percentile"] = memory_percentiles[
                percentile_list.index(p)
            ]

    duration_percentiles, err = duration_stats(duration_txt_location, percentile_list)
    if err != 0:
        log.warning(f"Function {function_name} duration stats not collected")
        e = -1
    else:
        log.debug(f"Function {function_name} duration stats collected")
        for p in percentile_list:
            function["duration"][f"{p}-percentile"] = duration_percentiles[
                percentile_list.index(p)
            ]

    cpu_percentiles, err = cpu_stats(cpu_txt_location, percentile_list)
    if err != 0:
        log.warning(f"Function {function_name} cpu stats not collected")
        e = -1
    else:
        log.debug(f"Function {function_name} cpu stats collected")
        for p in percentile_list:
            function["cpu"][f"{p}-percentile"] = cpu_percentiles[
                percentile_list.index(p)
            ]

    if e == 0:
        log.info(f"Profile completed. Statistics collected\n")
    else:
        log.warning(f"Function {function_name} statistics NOT collected completely")

    return function, e
