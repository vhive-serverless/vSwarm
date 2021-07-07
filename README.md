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
    is for benchmark utility _services_ (e.g. TimeseriesDB and XDT).
    - `timeseriesdb/`
- `tools/` \
    is for command-line tools.
    - `invoker/`
- `libs/`
    is for libraries used by benchmarks, utilities, and/or tools.
    - `vhivemetadata/`
        is for the Go library for handling vhivemetadata field.
    - `protos/`
        is for protobuf files and their generated outputs.
        - `timeseriesdb/`
        - `helloworld/`
    - `tracing/`
        is for tracing libraries in different programming language.
        - `go/`
        - `python/`
- `runner/` \
    is for setting up self-hosted GitHub Actions runners.