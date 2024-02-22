# Profiler 

This directory contains the profiling tool that profiles the CPU, memory utilization and duration of the benchmark functions. It reads the target functions (and their configurations) specified inside the input file (`config.json` by default) and then writes the profiles to an output file (`profile.json` by default) for further analysis. There are runtime arguments (e.g., RPS or requests-per-second target, experiment duration, sampling frequency) that you can specify if necessary.

## Setup:
The profiler utilizes the single node stock-only cluster setup as per [vHive quickstart guide](https://github.com/vhive-serverless/vhive/blob/main/docs/quickstart_guide.md) and [vHive developer guide](https://github.com/vhive-serverless/vHive/blob/main/docs/developers_guide.md). Currently, the tool can profile only _Serving Functions_ that are _NOT Pipelined_.

### Following functions can be profiled:
* `aes-go`, `aes-go-tracing`, `aes-python`, `aes-python-tracing`, `aes-nodejs`, `aes-nodejs-tracing`
* `auth-go`, `auth-go-tracing`, `auth-python`, `auth-python-tracing`, `auth-nodejs`, `auth-nodejs-tracing`
* `fibonacci-go`, `fibonacci-go-tracing`, `fibonacci-python`, `fibonacci-python-tracing`, `fibonacci-nodejs`, `fibonacci-nodejs-tracing`
* `gptj-python`
* `hotel-app-geo`, `hotel-app-profile`, `hotel-app-recommendation`, `hotel-app-reservation`, `hotel-app-user`, `hotel-app-geo-tracing`
* `adservice`, `cartservice`, `currencyservice`, `emailservice`, `paymentservice`, `productcatalogservice`, `shippingservice`
### Following functions cannot be profiled:
* `chained-function-eventing`: Eventing functions cannot be profiled
* `video-analytics`, `chained-function-serving`, `hotel-app:rate`, `hotel-app:search`, `hotel-app:search-tracing`, `onlineshop:checkoutservice`, `onlineshop:recommendationservice` : Pipelined functions cannot be profiled. 

### Python packages
```bash
pip3 install numpy jq typing matplotlib argparse PyYAML
```

## Profiling

```bash
python3 main.py profile -h
usage: main.py profile [-h] [-dbg bool] [-metset path] [-yaml path] [-build path] [-config path] [-o path]
                       [-rps float] [-iter integer] [-dur float]

optional arguments:
  -h, --help            show this help message and exit
  -dbg bool, --dbg bool
                        Set logger level to debug. Default: False
  -metset path, --metrics_server path
                        Path to Metrics Server YAML deployment file. Default: metrics-server/components.yaml
  -build path, --build path
                        Path to build files. Temporary location to build. Default: build
  -config path, --config_file path
                        Config file location. Default: config.json
  -o path, --output_json path
                        Output file location. Default: profile.json
  -rps float, --rps float
                        RPS at which functions must be invoked. Default: 0.2
  -iter integer, --sample_iter integer
                        Number of sample iterations. Default: 5
  -dur float, --run_duration float
                        Run Duration. Default: 100
```

### Command:
```bash
python3 main.py profile
```

The functions to be profiled are stored in an input JSON file named `config.json` by default(the user can utilize `-config` or `--config_file` to change this argument). The standard structure of this file is a list of json objects: a list of `predeployment-commands`, `postdeployment-commands` and `yaml-location`. 

An example input file can look like this:
```json
[
  {
    "yaml-location": "../../benchmarks/aes/yamls/knative/kn-aes-go.yaml",
    "predeployment-commands": [],
    "postdeployment-commands": []
  },
  {
      "yaml-location": "../../benchmarks/hotel-app/yamls/knative/kn-recommendation.yaml",
      "predeployment-commands": [
          "kubectl apply -f ../../benchmarks/hotel-app/yamls/knative/database.yaml",
          "kubectl apply -f ../../benchmarks/hotel-app/yamls/knative/memcached.yaml"
      ],
      "postdeployment-commands": []
  }
]
```
During deployment of the function to be profiled, the list of commands in `predeployment-commands` will be executed, followed by `kubectl apply -f <yaml-location>` and finally, the commands mentioned in `postdeployment-commands` will be executed. If `predeployment-commands` or `postdeployment-commands` objects are not included, no command will be executed pre or post the `kubectl apply` command. 

The profiles of the functions are stored in an output JSON file, named `profile.json` by default(the user can utilize `-o` or `--output_json` to change this argument). The generated profile contains the percentile averages of the CPU(millicpu), memory utilization(MiB) and the durations(milliseconds) of the function invocations.

An example output profile file can look like this
```json
{
    "aes-go": {
        "name": "aes-go",
        "yaml": "../../benchmarks/aes/yamls/knative/kn-aes-go.yaml",
        "cpu": {
            "0-percentile": 3.0,
            "1-percentile": 3.0,
            "5-percentile": 3.0,
            "25-percentile": 3.0,
            "50-percentile": 3.0,
            "75-percentile": 3.067513368983957,
            "95-percentile": 3.2592044134727063,
            "99-percentile": 3.3013636363636363,
            "100-percentile": 3.3181818181818183
        },
        "memory": {
            "0-percentile": 18.0,
            "1-percentile": 18.0,
            "5-percentile": 18.35833333333333,
            "25-percentile": 21.039772727272727,
            "50-percentile": 22.798418972332016,
            "75-percentile": 23.84157754010695,
            "95-percentile": 24.490853658536587,
            "99-percentile": 24.625681818181818,
            "100-percentile": 24.65909090909091
        },
        "duration": {
            "0-percentile": 0.584,
            "1-percentile": 0.5921066666666667,
            "5-percentile": 0.6337438888888888,
            "25-percentile": 0.6867670289855072,
            "50-percentile": 0.7153520757020757,
            "75-percentile": 0.7434741830065361,
            "95-percentile": 0.7660032945736434,
            "99-percentile": 0.7746408364195596,
            "100-percentile": 0.7849611111111113
        }
    }
}
```

The tool runs the `invoker` at a steady RPS (0.2 requests-per-second by default) and simultaneously monitors the CPU and memory utilization of the pod of the function being profiled. Users can utilize `-rps` or `--rps` to change the invocation rate, but it is highly recommended that the RPS < 0.5 to avoid creating multiple pod instances (as it might interfere with the profiling). The duration of the experiment can be changed using `-dur` or `--run_duration` flags. Users can also change the number of CPU and memory sampling points using `-iter` or `--sample_iter` flags. 

The profiling tool utilizes the `kubectl top command` to measure the CPU and memory utilization of the functions. This command requires `metrics-server` to be deployed. The YAML file for metrics-server is located at `./metrics-server/components.yaml` (User can utilize `-metset` or `--metrics_server` to change this path). The metrics-server is configured to monitor the utilization every 15 seconds. Hence, it is recommended that the number of sampling points be given such that the time between samples(duration/sample_iter) is greater than 15s to avoid oversampling. 

## Plotting

```bash
python3 main.py plot -h
usage: main.py plot [-h] [-i path] [-o path]

optional arguments:
  -h, --help            show this help message and exit
  -i path, --stat_file path
                        JSON file where profile details are stored
  -o path, --png_folder path
                        Output folder where plots are stored
```

The tool can also plot the generated profiles as a histogram. The command takes the `profile.json` file (`-i` or `--stat_file`) created during the profiling process as input and saves the histogram PNG files at the `png/` folder (`-o` or `--png_folder` flags) 

Example:
### Command:
```bash
python3 main.py plot
```
![image](https://github.com/vhive-serverless/vSwarm/assets/70060966/c10ef1a0-6586-4924-b7b3-112d85b05da3)
![image](https://github.com/vhive-serverless/vSwarm/assets/70060966/f16fbc0a-036c-4f0f-b7e7-d5e75c1cab82)


