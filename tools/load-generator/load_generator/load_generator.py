import numpy as np
import random

from log_config import *
from typing import Tuple

ONE_SECOND_TO_MICROSECONDS = 1000000
ONE_MINUTE_TO_SECONDS = 60


def generate_random_fp(distribution: str) -> float:
    """
    Generate random floating point based on distribution.

    Parameters:
    - `distribution`: Probability distribution based on which random number is generated: `exponential` or `uniform`

    Returns:
    - `float`: Random number
    """
    if distribution == "exponential":
        lamda_parameter = 0.5
        random_numbers = abs(
            np.random.exponential(scale=1 / lamda_parameter, size=1000)
        )
        normalized_numbers = (random_numbers - np.min(random_numbers)) / (
            np.max(random_numbers) - np.min(random_numbers)
        )
        return normalized_numbers[0]

    elif distribution == "uniform":
        return random.uniform(0.0, 1.0)


def generate_iat_per_granularity(
    number_of_invocations: int, iat_distribution: str, minute_granularity: bool
) -> list:
    """
    Given number of invocations in a unit time, and the distribution of inter-arrival times, this returns a list
    of timestamps as microseconds at which the invocation should take place.

    Parameters:
    - `number_of_invocations` (int): Number of invocations within unit time
    - `iat_distribution` (str): Can be `exponential` or `uniform` or `equidistant`
    - `minute_granularity` (bool): `True` if it is minute granularity. `False` if it is second granularity

    Returns:
    - `list`: List of invocation timestamps in microseconds at which the invocation should take place
    """
    if number_of_invocations == 0:
        return []

    # If number_of_invocations is not integer
    if not isinstance(number_of_invocations, int):
        log.warning(f"Given number of invocations is not integer. Illegal value")
        return []

    # Depending on the distribution get unity normalized invocation timestamps
    iat_result = []
    for i in range(number_of_invocations):
        if iat_distribution == "exponential":
            iat = generate_random_fp("exponential")
        elif iat_distribution == "uniform":
            iat = generate_random_fp("uniform")
        elif iat_distribution == "equidistant":
            iat = i / number_of_invocations
        else:
            log.warning(
                f"Invalid IAT Distribution: {iat_distribution}. Switching to uniform distribution"
            )
            iat = generate_random_fp("uniform")
        iat_result.append(iat)

    iat_result.sort()
    # Normalize to one second
    iat_result = [iat * ONE_SECOND_TO_MICROSECONDS for iat in iat_result]
    # Normalize to one minute
    if minute_granularity:
        iat_result = [iat * ONE_MINUTE_TO_SECONDS for iat in iat_result]
    iat_result = [int(iat) for iat in iat_result]

    return iat_result


def get_invocation_timestamp(
    trace_functions: dict, iat_distribution: str, minute_granularity: bool
) -> dict:
    """
    The function reads the `num-of-invocations` element of each function which is a list containing the
    number of invocations of the function every minute/second. It then finds the invocation timestamp as microsecond
    at which the invocation should take place based on the distribution of inter-arrival times.

    Parameters:
    - `trace_functions` (dict): Dictionary containing information about trace functions
    - `iat_distribution` (str): Can be `exponential` or `uniform` or `equidistant`
    - `minute_granularity` (bool): `True` if it is minute granularity. `False` if it is second granularity

    Returns:
    - `trace_functions` (dict): Updated dictionary containing invocation timestamps.
    """

    for function_name in trace_functions:

        if "num-of-invocations" not in trace_functions[function_name]:
            log.warning(
                f"Number of invocation details missing for function: {function_name}"
            )
            continue

        # For every second/minute, find the invocation timestamp and append it
        invocation_timestamps = []
        for number_of_invocations in trace_functions[function_name][
            "num-of-invocations"
        ]:
            invocation_timestamps.append(
                generate_iat_per_granularity(
                    number_of_invocations, iat_distribution, minute_granularity
                )
            )

        trace_functions[function_name]["invocation-timestamps"] = invocation_timestamps

    return trace_functions


def generate_load_timestamp(trace_functions: dict, duration: int) -> list:
    """
    This generates the load: timestamp and the endpoint at when the function has to be invoked.

    Parameters:
    - `trace_functions` (dict): Dictionary containing information about trace functions
    - `duration` (int): Number of minutes/seconds for which the load is to be generated

    Returns:
    - `list`: The function returns a list of dictionaries, with each element in list corresponding to
    invocation details in that unit time (minute/second) as a dictionary with keys `timestamp` and
    `endpoint`. 
    """

    load = []

    for minute in range(duration):
        # For each minute of the duration

        # Make a entry list of all the invocation timestamps of all the functions and store it
        # as a dictionary, with the timestamp as the key
        invocations_dict = {}
        for function_name in trace_functions:
            # If timestamp details are not found
            if "invocation-timestamps" not in trace_functions[function_name]:
                log.warning(
                    f"Invocation Timestamp details not found for function {function_name} for the {minute}th unit time"
                )
                continue
            # If duration of the experiment is longer than the available timestamps
            if (
                minute
                > len(trace_functions[function_name]["invocation-timestamps"]) - 1
            ):
                log.warning(
                    f"Mentioned duration is longer than the invocation-timestamp details found for the function {function_name}"
                )
                continue
            for iat in trace_functions[function_name]["invocation-timestamps"][minute]:
                # If proxy-function-endpoint is not available
                if "proxy-function-endpoint" not in trace_functions[function_name]:
                    log.warning(
                        f"Proxy endpoint for the function {function_name} not found"
                    )
                    continue
                invocations_dict[iat] = trace_functions[function_name][
                    "proxy-function-endpoint"
                ]

        timestamps = list(invocations_dict.keys())
        timestamps.sort()
        endpoints = []
        for t in timestamps:
            endpoints.append(invocations_dict[t])

        load.append({"timestamp": timestamps, "endpoint": endpoints})

    return load
