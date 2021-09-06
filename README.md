[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# vHive Benchmarking Suite

Welcome! This repository presents a collection of ready-to-run serverless benchmarks, each 
typically consisting of a number of interconnected serverless functions, and with a general
focus on realistic data-intensive workloads.

## Directory Structure

- `benchmarks` contains all of the available benchmark source code and manifests. 
- `utils` contains utilities for use within serverless functions, e.g. the tracing module.
- `tools` is for command-line tools and services useful outside of serverless functions, such as 
   deployment or invokation.
- `runner` is for setting up self-hosted GitHub Actions runners.

## Running Benchmarks

Details on each specific benchmark can be found in their relative subfolders. Every benchmark can 
be run on a knative cluster, and most can also be run locally with `docker-compose`. Please see the
[running benchmarks document](/docs/running_benchmarks.md) for detailed instructions on how to
run a benchmark locally or on a cluster.

## Contributing a Benchmark

We openly welcome any contributions, so please get in touch if you're interested!

Bringing up a benchmark typically consists of dockerizing the benchmark functions to deploy and
test them with docker-compose, then integrating the functions with knative, and including the
benchmark in the CI/CD pipeline. Please refer to our documentation on 
[bringing up new benchmarks](https://github.com/ease-lab/vhive/blob/main/docs/benchmarking/adding_benchmarks.md)
for more guidance.

We also have some basic requirements for contributions the the repository, which are described
in detail in our 
[Contributing to vHive](https://github.com/ease-lab/vhive/blob/main/docs/contributing_to_vhive.md)
document.