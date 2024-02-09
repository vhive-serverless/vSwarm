import csv
import os

from collections import OrderedDict
from log_config import *
from typing import Tuple


def read_durations_csv(directory_name: str) -> Tuple[dict, int]:
    """
    Read the durations.csv file and return the data.

    Parameters:
    - `directory_name` (str): Directory at which durations.csv file exists

    Returns:
    - `dict`: Dictionary of functions with details on their durations
    - `int`: 0 if no error. -1 if error
    """

    file_path = directory_name + "/durations.csv"

    # If file does not exist, then throw error and return
    if os.path.exists(file_path):
        log.info(f"{file_path} exists. Accessing information")
    else:
        log.error(f"durations.csv file not found at {file_path}")
        return {}, -1

    functions = OrderedDict()

    try:
        # Parse through the file
        with open(file_path, "r") as csv_file:

            # Create a CSV reader object
            csv_reader = csv.reader(csv_file)

            # Read the first row to obtain the header information
            first_row = next(csv_reader)
            if len(first_row) != 14:
                log.error(f"Illegal header: {file_path}")
                return {}, -1
            try:
                hashowner_index = first_row.index("HashOwner")
                hashapp_index = first_row.index("HashApp")
                hashfunction_index = first_row.index("HashFunction")
                average_index = first_row.index("Average")
                count_index = first_row.index("Count")
                minimum_index = first_row.index("Minimum")
                maximum_index = first_row.index("Maximum")
                percentile0_index = first_row.index("percentile_Average_0")
                percentile1_index = first_row.index("percentile_Average_1")
                percentile25_index = first_row.index("percentile_Average_25")
                percentile50_index = first_row.index("percentile_Average_50")
                percentile75_index = first_row.index("percentile_Average_75")
                percentile99_index = first_row.index("percentile_Average_99")
                percentile100_index = first_row.index("percentile_Average_100")
            except KeyError as e:
                log.error(f"Expected header information not available. Error: {e}")
                return {}, -1

            for index, row in enumerate(csv_reader):
                # Check if legal row:
                if len(row) != 14:
                    log.warning(
                        f"Illegal entry: {file_path}. Line Number: {index}. Information regarding the function not obtained"
                    )
                    continue

                function_name = (
                    row[hashowner_index] + row[hashapp_index] + row[hashfunction_index]
                )  # HashOwner + HashApp + HashFunction
                functions[function_name] = {}
                functions[function_name]["name"] = function_name
                functions[function_name]["duration"] = {}

                # Read through all the necessary fields and obtain information
                try:
                    functions[function_name]["duration"]["average"] = float(
                        row[average_index]
                    )
                    functions[function_name]["duration"]["count"] = float(
                        row[count_index]
                    )
                    functions[function_name]["duration"]["minimum"] = float(
                        row[minimum_index]
                    )
                    functions[function_name]["duration"]["maximum"] = float(
                        row[maximum_index]
                    )
                    functions[function_name]["duration"]["0-percentile"] = float(
                        row[percentile0_index]
                    )
                    functions[function_name]["duration"]["1-percentile"] = float(
                        row[percentile1_index]
                    )
                    functions[function_name]["duration"]["25-percentile"] = float(
                        row[percentile25_index]
                    )
                    functions[function_name]["duration"]["50-percentile"] = float(
                        row[percentile50_index]
                    )
                    functions[function_name]["duration"]["75-percentile"] = float(
                        row[percentile75_index]
                    )
                    functions[function_name]["duration"]["99-percentile"] = float(
                        row[percentile99_index]
                    )
                    functions[function_name]["duration"]["100-percentile"] = float(
                        row[percentile100_index]
                    )
                except ValueError as e:
                    log.warning(
                        f"Illegal entry: {file_path}. Line Number: {index}. Information regarding the function not obtained. Error: {e}"
                    )
                    del functions[function_name]
                    continue

    except Exception as e:
        log.error(f"Reading {file_path} failed. Durations of functions not obtained")
        return {}, -1

    log.info("Durations of functions obtained")
    return functions, 0


def read_memory_csv(directory_name: str) -> Tuple[dict, int]:
    """
    Read the memory.csv file and return the data.

    Parameters:
    - `directory_name` (str): Directory at which memory.csv file exists

    Returns:
    - `dict`: Dictionary of functions with details on their memory
    - `int`: 0 if no error. -1 if error
    """

    file_path = directory_name + "/memory.csv"

    # If file does not exist, then throw error and return
    if os.path.exists(file_path):
        log.info(f"{file_path} exists. Accessing information")
    else:
        log.error(f"memory.csv file not found at {file_path}")
        return {}, -1

    functions = OrderedDict()

    try:
        # Parse through the file
        with open(file_path, "r") as csv_file:

            # Create a CSV reader object
            csv_reader = csv.reader(csv_file)

            # Read the first row to obtain the header information
            first_row = next(csv_reader)
            if len(first_row) != 13:
                log.error(f"Illegal header: {file_path}")
                return {}, -1
            try:
                hashowner_index = first_row.index("HashOwner")
                hashapp_index = first_row.index("HashApp")
                hashfunction_index = first_row.index("HashFunction")
                count_index = first_row.index("SampleCount")
                average_index = first_row.index("AverageAllocatedMb")
                percentile1_index = first_row.index("AverageAllocatedMb_pct1")
                percentile5_index = first_row.index("AverageAllocatedMb_pct5")
                percentile25_index = first_row.index("AverageAllocatedMb_pct25")
                percentile50_index = first_row.index("AverageAllocatedMb_pct50")
                percentile75_index = first_row.index("AverageAllocatedMb_pct75")
                percentile95_index = first_row.index("AverageAllocatedMb_pct95")
                percentile99_index = first_row.index("AverageAllocatedMb_pct99")
                percentile100_index = first_row.index("AverageAllocatedMb_pct100")
            except KeyError as e:
                log.error(f"Expected header information not available. Error: {e}")
                return {}, -1

            for index, row in enumerate(csv_reader):
                # Check if legal row:
                if len(row) != 13:
                    log.warning(
                        f"Illegal entry: {file_path}. Line Number: {index}. Information regarding the function not obtained"
                    )
                    continue

                function_name = (
                    row[hashowner_index] + row[hashapp_index] + row[hashfunction_index]
                )  # HashOwner + HashApp + HashFunction
                functions[function_name] = {}
                functions[function_name]["name"] = function_name
                functions[function_name]["memory"] = {}

                # Read through all the necessary fields and obtain information
                try:
                    functions[function_name]["memory"]["count"] = float(
                        row[count_index]
                    )
                    functions[function_name]["memory"]["averag"] = float(
                        row[average_index]
                    )
                    functions[function_name]["memory"]["1-percentile"] = float(
                        row[percentile1_index]
                    )
                    functions[function_name]["memory"]["5-percentile"] = float(
                        row[percentile5_index]
                    )
                    functions[function_name]["memory"]["25-percentile"] = float(
                        row[percentile25_index]
                    )
                    functions[function_name]["memory"]["50-percentile"] = float(
                        row[percentile50_index]
                    )
                    functions[function_name]["memory"]["75-percentile"] = float(
                        row[percentile75_index]
                    )
                    functions[function_name]["memory"]["95-percentile"] = float(
                        row[percentile95_index]
                    )
                    functions[function_name]["memory"]["99-percentile"] = float(
                        row[percentile99_index]
                    )
                    functions[function_name]["memory"]["100-percentile"] = float(
                        row[percentile100_index]
                    )
                except ValueError as e:
                    log.warning(
                        f"Illegal entry: {file_path}. Line Number: {index}. Information regarding the function not obtained. Error: {e}"
                    )
                    del functions[function_name]
                    continue

    except Exception as e:
        log.error(
            f"Reading {file_path} failed. Memory Utilization of functions not obtained"
        )
        return {}, -1

    log.info("Memory of functions obtained")
    return functions, 0


def read_invocations_csv(directory_name: str) -> Tuple[dict, int]:
    """
    Read the invocations.csv file and return the data.

    Parameters:
    - `directory_name` (str): Directory at which invocations.csv file exists

    Returns:
    - `dict`: Dictionary of functions with details on their invocations
    - `int`: 0 if no error. -1 if error
    """

    file_path = directory_name + "/invocations.csv"

    # If file does not exist, then throw error and return
    if os.path.exists(file_path):
        log.info(f"{file_path} exists. Accessing information")
    else:
        log.error(f"invocations.csv file not found at {file_path}")
        return {}, -1

    functions = OrderedDict()

    try:
        # Parse through the file
        with open(file_path, "r") as csv_file:

            # Create a CSV reader object
            csv_reader = csv.reader(csv_file)  # Create a CSV reader object

            # Read the first row to obtain the header information
            first_row = next(csv_reader)
            if len(first_row) <= 4:
                log.error(f"Illegal header: {file_path}")
                return {}, -1
            try:
                hashowner_index = first_row.index("HashOwner")
                hashapp_index = first_row.index("HashApp")
                hashfunction_index = first_row.index("HashFunction")
                trigger_index = first_row.index("Trigger")
            except KeyError as e:
                log.error(f"Expected header information not available. Error: {e}")
                return {}, -1

            for index, row in enumerate(csv_reader):
                # Check if legal row:
                if len(row) <= 4:
                    log.warning(
                        f"Illegal entry: {file_path}. Line Number: {index}. Information regarding the function not obtained"
                    )
                    continue

                function_name = (
                    row[hashowner_index] + row[hashapp_index] + row[hashfunction_index]
                )  # HashOwner + HashApp + HashFunction
                functions[function_name] = {}
                functions[function_name]["name"] = function_name
                functions[function_name]["trigger"] = row[trigger_index]

                # Read through all the necessary fields and obtain information
                try:
                    invocation = row[4:]
                    invocation = [int(i) for i in invocation]
                    functions[function_name]["num-of-invocations"] = invocation
                except ValueError as e:
                    log.warning(
                        f"Illegal entry: {file_path}. Line Number: {index}. Information regarding the function not obtained. Error: {e}"
                    )
                    del functions[function_name]
                    continue

    except Exception as e:
        log.error(f"Reading {file_path} failed. Invocations of functions not obtained")
        return {}, -1

    log.info("Invocations of functions obtained")
    return functions, 0


def load_trace(directory_name: str) -> Tuple[dict, int]:
    """
    Read the CSV files and return the trace.

    Parameters:
    - `directory_name` (str): Directory at which CSV files exists

    Returns:
    - `dict`: Dictionary of functions with memory, durations, invocation details obtains from CSV files
    - `int`: 0 if no error. -1 if error
    """

    durations_info, err = read_durations_csv(directory_name)
    if err == -1:
        log.critical("Loading trace failed")
        return {}, -1
    memory_info, err = read_memory_csv(directory_name)
    if err == -1:
        log.critical("Loading trace failed")
        return {}, -1
    invocations_info, err = read_invocations_csv(directory_name)
    if err == -1:
        log.critical("Loading trace failed")
        return {}, -1

    functions = OrderedDict()
    for function_name in durations_info.keys():
        try:
            functions[function_name] = durations_info[function_name].copy()
            functions[function_name].update(memory_info[function_name])
            functions[function_name].update(invocations_info[function_name])
        except Exception as e:
            log.warning(f"{function_name} information not obtained. Error: {e}")
            del functions[function_name]
            continue

    return functions, 0
