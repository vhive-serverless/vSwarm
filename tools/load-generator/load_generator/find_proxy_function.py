import numpy as np
import scipy.optimize as sp
import math

from collections import OrderedDict

from log_config import *
from typing import Tuple


def get_error(trace_function, proxy_function) -> float:
    """
    Returns a float value on how close the trace function is to the proxy function. Lower the value, better the correlation.
    Euclidean distance between normalized memory and duration is considered.

    Parameters:
    - `trace_function` (dict): Dictionary containing information regarding trace function
    - `proxy_function` (dict): Dictionary containing information regarding proxy function

    Returns:
    - `float`: closeness value
    """

    try:
        trace_memory = trace_function["memory"]["75-percentile"]
        proxy_memory = proxy_function["memory"]["75-percentile"]
        trace_duration = trace_function["duration"]["75-percentile"]
        proxy_duration = proxy_function["duration"]["75-percentile"]
    except KeyError as e:
        log.warning(f"Correlation cannot be found. Error: {e}")
        return math.inf

    # NOTE: Better Error mechanisms can be considered to improve the correlation
    # Currently only the 75%tile memory and duration are considered.
    # Euclidean distance between normalized memory and duration is considered
    try:
        if trace_memory == 0: trace_memory += 0.01
        if trace_duration == 0: trace_duration += 0.01
        diff_memory = (trace_memory - proxy_memory) / trace_memory
        diff_duration = (trace_duration - proxy_duration) / trace_duration
        error = math.sqrt((diff_memory) ** 2 + (diff_duration) ** 2)
        return error
    except ValueError as e:
        log.warning(f"Correlation cannot be found. Error: {e}")
        return math.inf


def get_proxy_function_using_linear_sum_assignment(
    trace_functions: dict, proxy_functions: dict
) -> Tuple[dict, int]:
    """
    Obtains the one-to-one mapped proxy function for every trace function
    
    Parameters:
    - `trace_functions` (dict): Dictionary containing information regarding trace functions
    - `proxy_functions` (dict): Dictionary containing information regarding proxy functions
    
    Returns:
    - `dict`: Dictionary containing information regarding trace functions with the associated proxy functions
    - `int`: 0 if no error. -1 if error
    """

    try:

        trace_functions = OrderedDict(trace_functions)
        proxy_functions = OrderedDict(proxy_functions)

        trace_list = []
        for tf in trace_functions:
            trace_list.append(trace_functions[tf])
            trace_functions[tf]["index"] = len(trace_list) - 1

        proxy_list = []
        for pf in proxy_functions:
            proxy_list.append(proxy_functions[pf])
            proxy_functions[pf]["index"] = len(proxy_list) - 1

        # Creating error matrix
        m, n = len(trace_functions.keys()), len(proxy_functions.keys())
        error_matrix = np.empty((m, n))

        # This utilized Jonker-Volgenant algorithm for Linear Sum assignment - scipy package
        # to calculate the best possible assignment for the trace functions
        # Time complexity : O(n^3) where n is the largest of number of rows/columns
        for i in range(m):
            for j in range(n):
                error_matrix[i, j] = get_error(trace_list[i], proxy_list[j])

        # Do the linear sum assignment problem
        row_indices, col_indices = sp.linear_sum_assignment(error_matrix)
        assignments = list(zip(row_indices, col_indices))

        # Go through the assignment solution
        for assignment in assignments:
            row_index = assignment[0]
            col_index = assignment[1]
            trace = ""
            proxy = ""
            for tf in trace_functions:
                if row_index == trace_functions[tf]["index"]:
                    trace = tf
                    break
            for pf in proxy_functions:
                if col_index == proxy_functions[pf]["index"]:
                    proxy = pf
                    break
            trace_functions[trace]["proxy-function"] = proxy
            trace_functions[trace]["proxy-correlation"] = get_error(
                trace_functions[trace], proxy_functions[proxy]
            )
            log.debug(
                f"Found proxy function for {trace}: {trace_functions[trace]['proxy-function']} with correlation: {trace_functions[trace]['proxy-correlation']}"
            )

        # Go through the trace functions to ensure proxy function exists. If not, then report
        for tf in trace_functions:
            if "proxy-function" not in trace_functions[tf]:
                log.warning(f"Mapping for function {tf} not found")
            elif trace_functions[tf]["proxy-function"] == "":
                log.warning(f"Mapping for function {tf} not found")

        # Deleting unnecessary stuffs
        for tf in trace_functions:
            del trace_functions[tf]["index"]
        for pf in proxy_functions:
            del proxy_functions[pf]["index"]

        return trace_functions, 0

    except Exception as e:
        log.error(f"Mapping through linear sum assignment failed. Error: {e}")
        return trace_functions, -1


def get_closest_proxy_function(
    trace_functions: dict, proxy_functions: dict
) -> Tuple[dict, int]:
    """
    Obtains the closest proxy function for every trace function
    
    Parameters:
    - `trace_functions` (dict): Dictionary containing information regarding trace functions
    - `proxy_functions` (dict): Dictionary containing information regarding proxy functions
    
    Returns:
    - `dict`: Dictionary containing information regarding trace functions with the associated proxy functions
    - `int`: 0 if no error. -1 if error
    """

    try:
        proxy_list = []
        for function_name in proxy_functions:
            proxy_list.append(proxy_functions[function_name])
            proxy_functions[function_name]["index"] = len(proxy_list) - 1

        for function_name in trace_functions:
            min_error = math.inf
            min_error_index = -1
            for i in range(0, len(proxy_list)):
                error = get_error(trace_functions[function_name], proxy_list[i])
                if error < min_error:
                    min_error = error
                    min_error_index = i

            if min_error == math.inf:
                log.warning(f"Proxy function for function {function_name} not found")
                continue

            trace_functions[function_name]["proxy-function"] = proxy_list[
                min_error_index
            ]["name"]
            trace_functions[function_name]["proxy-correlation"] = get_error(
                trace_functions[function_name], proxy_list[min_error_index]
            )
            log.debug(
                f"Found proxy function for {function_name}: {trace_functions[function_name]['proxy-function']} with correlation: {trace_functions[function_name]['proxy-correlation']}"
            )

        for function_name in proxy_functions:
            del proxy_functions[function_name]["index"]

        return trace_functions, 0

    except Exception as e:
        log.error(f"Finding closest proxy function failed. Error: {e}")
        return trace_functions, -1


# TODO: log and plot the errors/correlation


def get_proxy_function(
    trace_functions: dict, proxy_functions: dict, unique_assignment: bool
) -> Tuple[dict, int]:
    """
    Obtains the closest proxy function for every trace function
    
    Parameters:
    - `trace_functions` (dict): Dictionary containing information regarding trace functions
    - `proxy_functions` (dict): Dictionary containing information regarding proxy functions
    - `unique_assignment` (bool): If `True`, then trace-proxy function mapping is one-to-one, provided #(proxy functions) > #(trace functions)
    
    Returns:
    - `dict`: Dictionary containing information regarding trace functions with the associated proxy functions
    - `int`: 0 if no error. -1 if error
    """

    trace_functions = OrderedDict(trace_functions)
    proxy_functions = OrderedDict(proxy_functions)

    log.info(
        f"Lower the correlation value, the proxy function is a better proxy of the trace function"
    )

    if (unique_assignment) and (len(trace_functions) <= len(proxy_functions)):
        log.info(
            f"Getting One-To-One mapping between trace function and proxy function using Linear-Sum-Assignment"
        )
        trace_functions, err = get_proxy_function_using_linear_sum_assignment(
            trace_functions=trace_functions, proxy_functions=proxy_functions
        )
        if err == -1:
            log.error(
                f"One-To-One mapping between trace function and proxy function not obtained"
            )
            log.info(
                f"Getting closest proxy function for every trace function. Note: Mapping may not be unique"
            )
            trace_functions, err = get_closest_proxy_function(
                trace_functions=trace_functions, proxy_functions=proxy_functions
            )

    elif (unique_assignment) and (len(trace_functions) > len(proxy_functions)):
        log.warning(
            f"One-To-One mapping between trace function and proxy function not possible since number of trace functions is greater than available proxy functions"
        )
        log.info(
            f"Getting closest proxy function for every trace function. Note: Mapping may not be unique"
        )
        trace_functions, err = get_closest_proxy_function(
            trace_functions=trace_functions, proxy_functions=proxy_functions
        )

    else:
        log.info(
            f"Getting closest proxy function for every trace function. Note: Mapping may not be unique"
        )
        trace_functions, err = get_closest_proxy_function(
            trace_functions=trace_functions, proxy_functions=proxy_functions
        )

    if err == -1:
        log.critical(f"Mapping between trace function and proxy function not obtained")
        return trace_functions, -1

    return trace_functions, 0
