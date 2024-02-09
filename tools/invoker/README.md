# Invoker

The invoker is a tool commonly used for calling and testing deployed functions / benchmarks. It reads the target addresses specified inside the input file (`endpoints.json` by default), and then writes the measured latencies to an output file (`rps<RPS>_lat.csv` by default, where `<RPS>` is the observed requests-per-sec value) for further analysis.

There are runtime arguments (e.g., RPS or requests-per-second target, experiment duration) that you can specify if necessary.

### Input file

The addresses to be invoked are stored in an input json file, named `endpoints.json` by default. The standard structure of this file is a list of json objects which have a hostname. In the event that more than one object (i.e. more than one hostname) is included, then the provided addresses will be called by the invoker in a round-robin fashion.

An example input file can look like this:
```json
[
  {
    "hostname": "producer.chained-functions-serving.192.168.1.240.sslip.io"
  }
]
```

For knative eventing, the invokation of functions with the goal of measuring their latency is more difficult since the connection does not stay open until a response arrives. For this reason we have developed `TimeseriesDB`. To use the invoker with TimeseriesDB the input json object will need an additional matchers field, which is a mapping of CloudEvent attribute names and values that are sought in completion events to exist. Please refer to the [benchmarking methodology documentation](https://github.com/vhive-serverless/vSwarm/blob/main/docs/methodology.md) for additional information.

An example input file for eventing can look like this:
```json
[
  {
    "hostname": "producer.chained-functions-eventing.192.168.1.240.sslip.io",
    "eventing": true,
    "matchers": {
      "type": "greeting",
      "source": "consumer"
    }
  }
]
```

### Invoker usage
`make invoker` can be used to build a binary of the invoker. Once this and the input file are ready, calling `./invoker` will start the process.
> Note: You need to have go and protoc installed on your machine to build the invoker. Refer to [this](https://golang.org/doc/install) for installation instructions or our install scripts `./utils/install_go.sh` and `./utils/install_protoc.sh`.

Additional inputs can be provided to set the desired duration (`--time`), requests per second (`-rps`) or port (`-port`) to be used. `-dbg` can be set for extra debug logs, and additionally tracing can be enabled for the invoker using the boolean `-trace` flag, in which case the `-zipkin` option may also need to be used in order to specify the address of the zipkin span collector.

Example usage:
```bash
$> ./invoker -port 31080 -dbg
time="2021-08-24T14:47:47.408226132Z" level=debug msg="Debug logging is enabled"
time="2021-08-24T14:47:47.408323683Z" level=info msg="Reading the endpoints from the file: endpoints.json"
time="2021-08-24T14:47:47.408517689Z" level=debug msg="Invoking: $HOSTNAME:31080"
time="2021-08-24T14:47:48.408726119Z" level=debug msg="Invoking: $HOSTNAME:31080"
time="2021-08-24T14:47:49.408669362Z" level=debug msg="Invoking: $HOSTNAME:31080"
time="2021-08-24T14:47:50.409601652Z" level=debug msg="Invoking: $HOSTNAME:31080"
time="2021-08-24T14:47:51.409282809Z" level=debug msg="Invoking: $HOSTNAME:31080"
time="2021-08-24T14:47:52.409379749Z" level=info msg="Issued / completed requests: 5, 0"
time="2021-08-24T14:47:52.409461172Z" level=info msg="Real / target RPS: 0.60 / 1"
time="2021-08-24T14:47:52.409479751Z" level=info msg="Experiment finished!"
time="2021-08-24T14:47:52.409522576Z" level=info msg="The measured latencies are saved in rps0.60_lat.csv"
```
