[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# vSwarm - Serverless Benchmarking Suite

Welcome! vSwarm is a collection of ready-to-run serverless benchmarks, each
typically consisting of a number of interconnected serverless functions, and with a general
focus on realistic data-intensive workloads.

This suite is part of the [vHive Ecosystem](https://vhive-serverless.github.io/). Its a turnkey and fully
tested solution meant to used in conjunction with
[vHive](https://github.com/ease-lab/vhive), and is compatible with all technologies that it supports,
namely, containers, Firecracker and gVisor microVMs. The majority of benchmarks support distributed
tracing with [Zipkin](https://zipkin.io/) which traces both the infra components and the user
functions.

In addition to the multi-function benchmarks, the vSwarm suite contains a set of [standalone functions](./benchmarks/README.md#standalone-functions-benchmark-summary), which support both x86 and arm64 architectures. Most of the standalone functions are compatible with [vSwarm-u](https://github.com/vhive-serverless/vSwarm-u), which allows to run them in the [gem5](https://www.gem5.org/) cycle-accurate full-system CPU simulator and study microarchitectural implications of serverless computing.
the state-of-the-art research platform for system-and microarchitecture.
The standalone functions can therefore be used as microbenchmarks to first pin-point microarchitectural bottlenecks in execution of serverless workloads using [Top-Down](https://www.intel.com/content/www/us/en/develop/documentation/vtune-cookbook/top/methodologies/top-down-microarchitecture-analysis-method.html) analysis ([tool](https://github.com/andikleen/pmu-tools/wiki/toplev-manual)) on real hardware and then further explore and optimize these bottlenecks using the [gem5](https://www.gem5.org/) cycle-accurate simulator.


## Directory Structure

- `benchmarks` contains all of the available benchmark source code and manifests.
- `utils` contains utilities for use within serverless functions, e.g. the tracing module.
- `tools` is for command-line tools and services useful outside of serverless functions, such as
   deployment or invocation.
- `runner` is for setting up self-hosted GitHub Actions runners.
- `docs` contains additional documentation on a number of relevant topics.


## Summary of Benchmarks
- 2 microbenchmarks for benchmarking chained functions performance, data transfer performance in
various patterns (pipeline, scatter, gather), and using different communication medium (AWS S3
and inline transfers)
- 8 real-world benchmarks
   - MapReduce: [Corral](/benchmarks/corral) (golang), and an [aws-reference](/benchmarks/map-reduce)
    python implementation of Aggregation Query from the representative
    [AMPLab Big Data Benchmark](https://www.cs.cmu.edu/~pavlo/papers/benchmarks-sigmod09.pdf)
   1node dataset.
   - Real-time [video analytics](/benchmarks/video-analytics) (Python and Golang): recognizes objects in a video fragment
   - ML models training: [stacking ensemble training](/benchmarks/stacking-training) and
   [iterative hyperparameter tuning](/benchmarks/tuning-halving)
   - ExCamera video decoding (gg): decoding of a video in parallel
   - distributed compilation (gg): compiles LLVM in parallel
   - fibonacci (gg): classic recursive implementation to find `n`th number in the sequence by calculating `n-1` and `n-2` in parallel
 - 25 standalone functions
   - [AES](https://github.com/vhive-serverless/vSwarm/tree/main/benchmarks/aes), [Auth](https://github.com/vhive-serverless/vSwarm/tree/main/benchmarks/auth), [Fibonacci](https://github.com/vhive-serverless/vSwarm/tree/main/benchmarks/fibonacci): Same functionality implemented in the three different runtimes: Python, NodeJS, Golang.
   - [Online shop](https://github.com/vhive-serverless/vSwarm/tree/main/benchmarks/online-shop): 9 functions implemented in various runtimes, ported from Googles [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo)
   - [Hotel reservation](https://github.com/vhive-serverless/vSwarm/tree/main/benchmarks/hotel-app): 7 microservices from DeathStarBenchs [Hotel Reservation Application](https://github.com/delimitrou/DeathStarBench/tree/master/hotelReservation) ported as standalone serverless microbenchmarks.

Refer to [this document](/benchmarks/README.md) for more detail on the differences and supported features of each benchmark.


## Running Benchmarks

Details on each specific benchmark can be found in their relative subfolders. Every benchmark can
be run on a knative cluster, and most can also be run locally with `docker-compose`. Please see the
[running benchmarks document](/docs/running_benchmarks.md) for detailed instructions on how to
run a benchmark locally or on a cluster.

We have a detailed outline on the benchmarking methodology used, which you can find [here](/docs/methodology.md).


## Contributing a Benchmark

We openly welcome any contributions, so please get in touch if you're interested!

Bringing up a benchmark typically consists of dockerizing the benchmark functions to deploy and
test them with docker-compose, then integrating the functions with knative, and including the
benchmark in the CI/CD pipeline. Please refer to our documentation on
[bringing up new benchmarks](/docs/adding_benchmarks.md)
for more guidance.

We also have some basic requirements for contributions the the repository, which are described
in detail in our
[Contributing to vHive](/docs/contributing_to_vhive.md)
document.


## License and copyright

vSwarm is free. We publish the code under the terms of the MIT License that allows distribution, modification, and commercial use.
This software, however, comes without any warranty or liability.

The software is maintained by the [vHive Ecosystem](https://vhive-serverless.github.io/), [EASE lab](https://easelab.inf.ed.ac.uk/) the University of Edinburgh,
[Stanford Systems and Networking Research](https://github.com/StanfordSNR).


### Maintainers

- Invoker, timeseriesdb, runners - Dmitrii Ustiugov: [GitHub](https://github.com/ustiugov),
[twitter](https://twitter.com/DmitriiUstiugov/), [web page](https://ustiugov.github.io)
- Corral Benchmark - Dmitrii Ustiugov: [GitHub](https://github.com/ustiugov),
[twitter](https://twitter.com/DmitriiUstiugov/), [web page](https://ustiugov.github.io)
- Map-Reduce, Stacking-training and Tuning-halving - Alan Nair [GitHub](https://github.com/alannair)
- Chained Functions and Video analytics - Shyam Jesalpura [GitHub](https://github.com/shyamjesal)
- GG benchmarks - Shyam Jesalpura [GitHub](https://github.com/shyamjesal)
- Standalone functions - David Schall [GitHub](https://github.com/dhschall),[web page](https://dhschall.github.io/)
- Multi cloud containers (lambda) - Alan Nair [GitHub](https://github.com/alannair)
