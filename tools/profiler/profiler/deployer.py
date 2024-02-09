import os
import stat
import subprocess

import json
import yaml
import time

from log_config import *
from typing import Tuple


def check_shell_path() -> int:
    """
    Check whether shell path is BASH or not.

    Returns:
    `int`: 0: No Error. -1: Error
    """
    shell_path = os.environ.get("SHELL")
    log.info(f"Shell path: {shell_path}")
    if "bash" not in shell_path:
        log.critical(f"{shell_path} is not BASH")
        return -1
    else:
        return 0


def deploy_metrics_server(metrics_server_yaml_location: str) -> int:
    """
    Deploys metrics server

    Parameters:
    - `metrics_server_yaml_location` (str): Metrics Server YAML location
    
    Returns:
    `int`: 0: No Error. -1: Error
    """

    # Deploy the metrics server
    try:
        deployment_command = f"kubectl apply -f {metrics_server_yaml_location}"
        result = subprocess.run(
            deployment_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.debug(
            f"{deployment_command} command completed with return code {result.returncode}"
        )
    except subprocess.CalledProcessError as e:
        log.critical(
            f"Metrics Server not deployed. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
        )
        return -1
    except Exception as e:
        log.critical(f"Metrics Server not deployed. Error: {e}")
        return -1

    # Get the pod status of metrics server
    def monitor_pods_to_check_metrics_server_deployed() -> int:
        try:
            get_podlist_command = f"kubectl get pods --all-namespaces --no-headers"
            result = subprocess.run(
                get_podlist_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            pods = result.stdout.decode("utf-8").strip().split("\n")
            for p in pods:
                if ("metrics-server" in p) and (p.split()[3] == "Running"):
                    return True
            return False
        except subprocess.CalledProcessError as e:
            log.warning(
                f"Metrics Server pod not running. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
            )
            return False
        except Exception as e:
            log.warning(f"Metrics Server pod not running. Error: {e}")
            return False

    # Monitor the pod list, until it is ready
    # Monitoring happens every 5 seconds for 15 minutes. If it shows failure even after that then it returns failure
    monitor_time = 15 * 60
    sleep_time = 5
    status = False
    for _ in range(int(monitor_time / sleep_time)):
        status = monitor_pods_to_check_metrics_server_deployed()
        if status:
            break
        else:
            time.sleep(sleep_time)

    if status:
        log.info(f"Metrics server deployed and running")
        return 0
    else:
        log.critical(f"Metrics server not running")
        return -1


def delete_all_services() -> int:
    """
    Deletes all services

    Returns:
    `int`: 0: No Error. -1: Error
    """

    # Delete all the services
    try:
        delete_service_command = f"kn service delete --all"
        result = subprocess.run(
            delete_service_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.debug(
            f"kn service delete command completed with return code {result.returncode}"
        )
    except subprocess.CalledProcessError as e:
        log.warning(
            f"Services not deleted. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
        )
        return -1
    except Exception as e:
        log.warning(f"Services not deleted. Error: {e}")
        return -1

    # Monitor the service list whether everything is deleted. Wait until all the services are deleted.
    def are_services_deleted() -> bool:
        try:
            get_servicelist_command = f"kn service list --no-headers"
            result = subprocess.run(
                get_servicelist_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            services = result.stdout.decode("utf-8").strip().split("\n")
            services = [s for s in services if s != ""]
            for s in services:
                if "No services found." in s:
                    return True
            return False
        except subprocess.CalledProcessError as e:
            log.warning(
                f"Service List can't be monitored. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
            )
            return False
        except Exception as e:
            log.warning(f"Service List can't be monitored. Error: {e}")
            return False

    # Monitor the service list, until all are deleted.
    # Monitoring happens every 2 second for 15 minutes. If it shows failure even after that then it returns failure
    monitor_time = 15 * 60
    sleep_time = 2
    status = False
    for _ in range(int(monitor_time / sleep_time)):
        status = are_services_deleted()
        if status:
            break
        else:
            time.sleep(sleep_time)

    if status:
        log.debug(f"All services deleted")
        return 0
    else:
        log.warning(f"Services not deleted. Note: Might affect later profiling stages")
        return -1


def deploy_service(
    yaml_filename: str,
    predeployment_commands: list,
    postdeployment_commands: list,
    build_shell_scripts_location: str,
) -> Tuple[str, int]:
    """
    Deploys the service

    Parameters:
    - `yaml_filename` (str): YAML file name and location
    - `predeployment_commands` (list) : List of commands to be run before deployment
    - `postdeployment_commands` (list) : List of commands to be run after deployment
    - `build_shell_scripts_location` (str): build folder location where shell scripts are stored

    Returns:
    - `function_name` (str): Function name as per YAML file
    - `int`: 0: No Error. -1: Error 
    """

    # Check whether yaml file exists or not.
    try:
        with open(yaml_filename, "r"):
            pass
    except FileNotFoundError:
        log.error(f"{yaml_filename} YAML file not found")
        return None, -1
    except Exception as e:
        log.error(f"{yaml_filename} YAML file not found. Error occured: {e}")
        return None, -1

    # Get the function name from yaml file
    function_name = None
    try:
        with open(yaml_filename, "r") as f:
            yaml_data = yaml.safe_load(f)
            function_name = yaml_data["metadata"]["name"]
    except KeyError as e:
        log.warning(
            f"Function name not found. KeyError:{e}. Switching to default name: function"
        )
        function_name = "function"
    except FileNotFoundError:
        log.error(f"{yaml_filename} YAML File not found")
        return None, -1
    except Exception as e:
        log.error(f"{yaml_filename} YAML File not found. An error occured: {e}")
        return None, -1

    # Check whether folder where shell scripts are to be located exists or not
    if not os.path.exists(build_shell_scripts_location):
        log.debug(f"{build_shell_scripts_location} directory does not exist.")
        os.makedirs(build_shell_scripts_location)
        log.debug(f"{build_shell_scripts_location} directory created")
    else:
        pass

    # Create a list of commands to be executed
    commands = []
    # Commands to be executed before deployment
    for c in predeployment_commands:
        commands.append(c + "\n")
    # Deployment command
    deployment_command = f"kubectl apply -f {yaml_filename}"
    commands.append(deployment_command + "\n")
    # Commands to be executed after deployment
    for c in postdeployment_commands:
        commands.append(c + "\n")

    # Get shell path
    shell_path = os.environ.get("SHELL")

    # Writing a shell script
    # Creating the shell script file name
    shell_filename = os.path.basename(yaml_filename).replace(".yaml", ".sh")
    shell_filename = f"{build_shell_scripts_location}/{shell_filename}"
    # Writing commands into the shell script
    with open(shell_filename, "w") as f:
        f.write(f"#!{shell_path}\n")
        for c in commands:
            f.write(c)
    # Setting executable permissions for the shell script
    # Permissions: -rwxr-xr-x
    os.chmod(
        shell_filename,
        stat.S_IRUSR
        | stat.S_IWUSR
        | stat.S_IXUSR
        | stat.S_IRGRP
        | stat.S_IXGRP
        | stat.S_IROTH
        | stat.S_IXOTH,
    )
    log.debug(f"{shell_filename} created")

    # Execute the shell script and deploy the function
    execute_shell = f"{shell_path} {shell_filename}"
    try:
        result = subprocess.run(
            execute_shell,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.debug(
            f"{shell_filename} executed successfully with return code: {result.returncode}"
        )
    except subprocess.CalledProcessError as e:
        log.error(
            f"{shell_filename} execution failed. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
        )
        return None, -1
    except Exception as e:
        log.error(f"{shell_filename} execution failed. Error: {e}")
        return None, -1

    # Given the function name, get the service status
    def get_service_status(function_name: str) -> bool:
        try:
            get_service_command = f"kn service list --no-headers"
            result = subprocess.run(
                get_service_command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            services = result.stdout.decode("utf-8").strip().split("\n")
            for s in services:
                try:
                    service_name = s.split()[0]
                    service_status = s.split()[8]
                except IndexError as e:
                    continue
                if function_name in service_name:
                    if service_status == "True":
                        return True
                    else:
                        return False
            return False
        except subprocess.CalledProcessError as e:
            log.warning(
                f"Service can't be monitored. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
            )
            return False
        except Exception as e:
            log.warning(f"Service can't be monitored. Error: {e}")
            return False

    # Monitor the service, until it is ready
    # Monitoring happens every 5 seconds for 15 minutes. If it shows failure even after that then it returns failure
    monitor_time = 15 * 60
    sleep_time = 5
    status = False
    for _ in range(int(monitor_time / sleep_time)):
        status = get_service_status(function_name)
        if status:
            break
        else:
            time.sleep(sleep_time)

    if status:
        log.info(f"Profiling function: {function_name}")
        log.debug(f"{yaml_filename}: {function_name} service deployed")
        return function_name, 0
    else:
        log.error(f"{yaml_filename}: {function_name} service not deployed")
        return function_name, -1


def get_endpoint(function_name: str, endpoint_file_location: str) -> Tuple[str, int]:
    """
    Gets the endpoint of the deployed function and stores it for invoker to invoke

    Parameters:
    - `function_name` (str): function name
    - `endpoint_file_location` (str): location at which the endpoint must be stored 

    Returns:
    - `endpoint` (str): Endpoint
    - `int`: 0: No Error. -1: Error
    """

    # Get list of all services
    get_service_command = f"kn service list --no-headers"
    try:
        result = subprocess.run(
            get_service_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        result = result.stdout.decode("utf-8").strip().split("\n")
    except subprocess.CalledProcessError as e:
        log.warning(
            f"Endpoints can't be collected. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
        )
        return None, -1
    except Exception as e:
        log.warning(f"Endpoints can't be collected. Error: {e}")
        return None, -1

    # Going through all the services and its corresponding listed URLs to find the correct url
    endpoint = None
    for r in result:
        try:
            service_name = r.split()[0]
            if service_name == function_name:
                endpoint = r.split()[1].replace("http://", "")
                break
        except IndexError:
            continue
        except Exception as e:
            log.warning(f"Error trying to find the correct endpoint : {e}")
            continue

    if endpoint == None:
        log.error(f"{function_name} Service Endpoint not found")
        return None, -1
    else:
        log.info(f"Service Endpoint: {endpoint}")

    # Convert the list to JSON format
    endpoint = [{"hostname": endpoint}]
    json_output = json.dumps(endpoint, indent=3)

    # Write the JSON output to endpoints.json
    # Check whether folder where endpoints are to be located exists or not
    if not os.path.exists(endpoint_file_location):
        log.debug(f"{endpoint_file_location} directory does not exist.")
        os.makedirs(endpoint_file_location)
        log.debug(f"{endpoint_file_location} directory created")
    else:
        pass

    json_file = open(f"{endpoint_file_location}/endpoints.json", "w")
    json_file.write(json_output)
    json_file.close()
    log.debug(f"{endpoint_file_location}/endpoints.json file written")

    return endpoint, 0


def delete_pod(pod_name: str) -> int:
    """
    Run command to delete the pod.

    Parameters:
    - `pod_name` (str): Pod name

    Returns:
    `int`: 0: No Error. -1: Error
    """
    delete_pod_command = f"kubectl delete pod {pod_name}"
    try:
        result = subprocess.run(
            delete_pod_command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        log.debug(
            f"{delete_pod_command} command executed successfully with return code: {result.returncode}"
        )
        return 0
    except subprocess.CalledProcessError as e:
        log.warning(
            f"Pod {pod_name} is not deleted by command. Waiting for the pod to be terminated automatically. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
        )
        return -1
    except Exception as e:
        log.warning(
            f"Pod {pod_name} is not deleted by command. Waiting for the pod to be terminated automatically. Error: {e}"
        )
        return -1






def wait_until_pod_is_deleted(pod_name: str) -> int:
    """
    Waits until the pod is deleted.

    Parameters:
    - `pod_name` (str): Pod name

    Returns:
    - `int`: 0: No Error. -1: Error
    """

    def is_pod_deleted(pod_name: str) -> bool:
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
                if p.strip() == "":
                    continue
                if pod_name == p.split()[0]:
                    return False
            return True
        except subprocess.CalledProcessError as e:
            log.warning(
                f"Pod List can't be obtained. I don't know whether pod {pod_name} is deleted or not. Return code: {e.returncode}. Error: {e.stderr.decode('utf-8')}"
            )
            return False
        except Exception as e:
            log.warning(
                f"Pod List can't be obtained. I don't know whether pod {pod_name} is deleted or not. Error: {e}"
            )
            return False

    # Monitor the pod list, until the pod is deleted.
    # Monitoring happens every 5 seconds for 15 minutes. If it shows failure even after that then it returns failure
    monitor_time = 15 * 60
    sleep_time = 5
    status = False
    for _ in range(int(monitor_time / sleep_time)):
        status = is_pod_deleted(pod_name)
        if status:
            break
        else:
            time.sleep(sleep_time)

    if status:
        log.debug(f"Pod {pod_name} deleted")
        return 0
    else:
        log.warning(f"Pod {pod_name} not deleted. Might interfere with later profiles")
        return -1
