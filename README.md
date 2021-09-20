[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


# vSwarm - Serverless Benchmarking Suite

Welcome! vSwarm is a collection of ready-to-run serverless benchmarks, each 
typically consisting of a number of interconnected serverless functions, and with a general
focus on realistic data-intensive workloads.

This suite is a turnkey and fully tested solution meant to used in conjunction with 
[vHive](https://github.com/ease-lab/vhive), and is compatible with all technologies that it supports,
namely, containers, Firecracker and gVisor microVMs. The majority of benchmarks support distributed
tracing with [Zipkin](https://zipkin.io/) which traces both the infra components and the user 
functions.


## Directory Structure

- `benchmarks` contains all of the available benchmark source code and manifests. 
- `utils` contains utilities for use within serverless functions, e.g. the tracing module.
- `tools` is for command-line tools and services useful outside of serverless functions, such as 
   deployment or invokation.
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

The software is maintained at the [EASE lab](https://easelab.inf.ed.ac.uk/) in the University of Edinburgh,
[Stanford Systems and Networking Research](https://github.com/StanfordSNR), and the vSwarm open-source community.


### Maintainers

- Invoker, timeseriesdb, runners - Dmitrii Ustiugov: [GitHub](https://github.com/ustiugov),
[twitter](https://twitter.com/DmitriiUstiugov), [web page](http://homepages.inf.ed.ac.uk/s1373190/)
- ML benchmarks and utils (tracing and storage modules) - Michal Baczun [GitHub](https://github.com/MBaczun)
- ML benchmarks - Rustem Feyzkhanov [GitHub](https://github.com/ryfeus)
- Video Analytics and Map-Reduce benchmarks - Shyam Jesalpura [GitHub](https://github.com/shyamjesal)
- GG benchmarks - Francisco Romero [GitHub](https://github.com/faromero) and Clemente Farias [GitHub](https://github.com/cbfariasc)
