# Loader

A load generator for serverless computing based upon [faas-load-generator](https://github.com/vSwarm/tools/faas-load-generator) and the example code of [vHive](https://github.com/ease-lab/vhive).

## Usage

For more details, please see `Makefile`.
### Execution
For hotstart, run the following
```sh
$ make build
$ ./load --rps <request-per-sec> --duration <1-to-60-min> 
```

OR 

```sh
$ make ARGS="./load --rps <request-per-sec> --duration <1-to-60-min>" run
```

As for explicit cold start, replace `run` above with `coldstart`. 

### Build the image for server function

```sh
$ make build image
```

:warning: The protocal and the python server in `\server\trace-func-py` are deprecated.

- [ ] Update the python server code.

### Update gRPC protocol

```sh
$ make proto
```

### Run experiments limiting RPS

```sh
$ bash scripts/run_rsp_range.sh <start-rps> <end-rps> <step-size> <duration> <cmd>
```