# vHive Benchmarking

## Directory Structure
- `benchmarks/` \
    is for benchmarks.
    - `<benchmark-name>/` \
        - `build-push.sh` \
            build and push all the Docker images of the benchmark.
        - `down.sh` \
            take the benchmark down and clean up synchronously.
        - `test.sh` \
            test the benchmark and indicate success with exit code 0.
        - `up.sh` \
            bring the benchmark up synchronously.
- `utils/` \
    is for utilities used within serverless functions.
    - `vhivemetadata/`
        is for the Go library for handling vhivemetadata field.
    - `protobuf/`
        is for common protobuf files and their generated outputs.
        - `helloworld/`
    - `tracing/`
        is for tracing libraries in different programming language.
        - `go/`
        - `python/`
- `tools/` \
    is for command-line tools and services useful outside of 
    serverless functions, such as for deployment or invokation.
    - `invoker/`
    - `timeseriesdb/`

- `runner/` \
    is for setting up self-hosted GitHub Actions runners.