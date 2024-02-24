import os
import stat
import subprocess

import string
import secrets

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
        log.info(f"All services deleted")
        return 0
    else:
        log.warning(f"Services not deleted.")
        return -1


def deploy_services(
    trace_functions: dict,
    proxy_functions: dict,
    config_file: str,
    build_shell_scripts_location: str,
) -> Tuple[dict, dict, int]:
    """
    Deploys the proxy services for every trace function

    Parameters:
    - `trace_functions` (dict): Dictionary of all the trace functions
    - `proxy_functions` (dict): Dictionary of all the proxy functions
    - `build_shell_scripts_location` (str): build folder location where shell scripts are stored
    - `config_file` (str): Path to the file containing configuration details of deploying the proxy functions
    
    Returns:
    - `trace_functions` (dict): Updated Dictionary of all the trace functions
    - `proxy_functions` (dict): Updated Dictionary of all the proxy functions
    - `int`: 0 if No Error. -1 if Error
    """

    def deploy_service(
        trace_function: dict, proxy_function: dict, build_shell_scripts_location: str
    ) -> Tuple[dict, int]:
        """
        Deploys the proxy service for the given trace function

        Parameters:
        - `trace_function` (dict): Dictionary containing details of the trace function
        - `proxy_function` (dict): Dictionary containing details of the proxy function
        - `build_shell_scripts_location` (str): build folder location where shell scripts are stored

        Returns:
        - `trace_function` (dict): Updated dictionary containing information regarding proxy service 
        - `int`: 0: No Error. -1: Error 
        """

        # Check whether yaml file exists or not.
        try:
            with open(pf["yaml"], "r"):
                pass
        except FileNotFoundError:
            log.error(f"{pf['yaml']} YAML file not found")
            return trace_function, -1
        except Exception as e:
            log.error(f"{pf['yaml']} YAML file can't be opened. Error occured: {e}")
            return trace_function, -1

        # Get the function name from yaml file
        yaml_function_name = None
        try:
            with open(pf["yaml"], "r") as f:
                yaml_data = yaml.safe_load(f)
                yaml_function_name = yaml_data["metadata"]["name"]
        except KeyError as e:
            log.warning(
                f"Function name not found. KeyError:{e}. Switching to default name: function"
            )
            yaml_function_name = "function"
        except Exception as e:
            log.error(f"{pf['yaml']} YAML File can't be opened. An error occured: {e}")
            return trace_function, -1

        # Creating a service, yaml file whose service name is unique
        characters = string.ascii_lowercase + string.digits
        random_string = "".join(secrets.choice(characters) for _ in range(32))
        yaml_function_name = yaml_function_name + "-" + random_string
        yaml_data["metadata"]["name"] = yaml_function_name
        trace_function["proxy-function-name"] = yaml_function_name

        basename = os.path.basename(pf["yaml"]).replace(".yaml", "")
        modified_yaml_filename = basename + "-" + random_string + ".yaml"
        modified_yaml_filename = (
            f"{build_shell_scripts_location}/{modified_yaml_filename}"
        )
        trace_function["proxy-function-yaml-location"] = modified_yaml_filename

        # The modified yaml file is then stored in build directory
        try:
            with open(modified_yaml_filename, "w") as yf:
                yaml.dump(yaml_data, yf, default_flow_style=False)
        except Exception as e:
            log.error(
                f"Error occured while creating the YAML file. Function {trace_function['name']} not deployed"
            )
            return trace_function, -1

        # Create a list of commands to be executed
        commands = []
        # Commands to be executed before deployment
        for c in pf["predeployment-commands"]:
            commands.append(c + "\n")
        # Deployment command
        deployment_command = f"kubectl apply -f {modified_yaml_filename}"
        commands.append(deployment_command + "\n")
        # Commands to be executed after deployment
        for c in pf["postdeployment-commands"]:
            commands.append(c + "\n")

        # Get shell path
        shell_path = os.environ.get("SHELL")

        # Writing a shell script
        # Creating the shell script file name
        shell_filename = basename + "-" + random_string + ".sh"
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
            return trace_function, -1
        except Exception as e:
            log.error(f"{shell_filename} execution failed. Error: {e}")
            return trace_function, -1

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
                    except IndexError:
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
            status = get_service_status(trace_function["proxy-function-name"])
            if status:
                break
            else:
                time.sleep(sleep_time)

        if status:
            log.debug(
                f"Proxy service for {trace_function['name']}: {trace_function['proxy-function-name']} service deployed"
            )
            return trace_function, 0
        else:
            log.error(
                f"Proxy service for {trace_function['name']} service not deployed"
            )
            return trace_function, -1


    # Check whether folder where shell scripts are to be located exists or not
    if not os.path.exists(build_shell_scripts_location):
        log.info(f"{build_shell_scripts_location} directory does not exist.")
        os.makedirs(build_shell_scripts_location)
        log.info(f"{build_shell_scripts_location} directory created")
    else:
        files = os.listdir(build_shell_scripts_location)
        for filename in files:
            file_path = os.path.join(build_shell_scripts_location, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                log.warning(f"File {file_path} not deleted")
        log.debug(f"Previous files in {build_shell_scripts_location} deleted")


    # If config file is available, then obtain the YAML filename, corresponding
    # predeployment and postdeployment commands from the config file.
    # If the config file is not available, then deploy the YAML file as mentioned in
    # the output.json file with default commands.

    utilize_config_file = False

    # Check whether the config file exists or not
    # If exists, then obtain information from that
    if os.path.exists(config_file):
        log.info(f"Config file {config_file} exists. Accessing information")
        try:
            with open(config_file, "r") as jf:
                data = json.load(jf)
            for function_dict in data:
                for function_name in proxy_functions:
                    if (
                        proxy_functions[function_name]["yaml"]
                        == function_dict["yaml-location"]
                    ):
                        try:
                            proxy_functions[function_name][
                                "predeployment-commands"
                            ] = function_dict["predeployment-commands"]
                        except KeyError:
                            proxy_functions[function_name][
                                "predeployment-commands"
                            ] = []
                        try:
                            proxy_functions[function_name][
                                "postdeployment-commands"
                            ] = function_dict["postdeployment-commands"]
                        except KeyError:
                            proxy_functions[function_name][
                                "postdeployment-commands"
                            ] = []
                        break
            utilize_config_file = True
        except Exception as e:
            log.warning(f"Config file {config_file} cannot be read. Error: {e}")

    if not utilize_config_file:
        log.info(
            f"Config file {config_file} does not exist. Deploying using default commands"
        )
        for function_name in proxy_functions:
            proxy_functions[function_name]["predeployment-commands"] = []
            proxy_functions[function_name]["postdeployment-commands"] = []

    for function_name in proxy_functions:
        if "predeployment-commands" not in proxy_functions[function_name]:
            proxy_functions[function_name]["predeployment-commands"] = []
        if "postdeployment-commands" not in proxy_functions[function_name]:
            proxy_functions[function_name]["postdeployment-commands"] = []

    for trace_function_name in trace_functions:
        tf = trace_functions[trace_function_name]
        proxy_function_name = tf["proxy-function"]
        try:
            pf = proxy_functions[proxy_function_name]
        except KeyError:
            log.error(f"{trace_function_name} excluded since proxy function not found")
            continue
        trace_functions[trace_function_name], _ = deploy_service(
            trace_function=tf,
            proxy_function=pf,
            build_shell_scripts_location=build_shell_scripts_location,
        )

    return trace_functions, proxy_functions, 0


def collect_endpoints(trace_functions: dict) -> Tuple[dict, int]:
    """
    Gets the endpoint of the deployed proxies of the trace functions 

    Parameters:
    - `trace_functions` (dict): Dictionary of all the trace functions

    Returns:
    - `trace_functions` (dict): Updated trace_functions dictionary containing information about endpoints of proxy services 
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
        return trace_functions, -1
    except Exception as e:
        log.warning(f"Endpoints can't be collected. Error: {e}")
        return trace_functions, -1

    # Going through all the services and its corresponding listed URLs to find the urls
    for r in result:
        try:
            service_name = r.split()[0]
            endpoint = r.split()[1].replace("http://", "")
            for function_name in trace_functions:
                if (
                    service_name
                    == trace_functions[function_name]["proxy-function-name"]
                ):
                    trace_functions[function_name]["proxy-function-endpoint"] = endpoint
                    break
        except IndexError:
            continue
        except Exception as e:
            log.warning(f"Error trying to find the correct endpoint : {e}")
            continue

    for function_name in trace_functions:
        if "proxy-function-endpoint" not in trace_functions[function_name]:
            log.error(
                f"Endpoint not found for the proxy of trace function: {function_name}"
            )

    return trace_functions, 0
