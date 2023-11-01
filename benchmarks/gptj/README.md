# Gptj Benchmark

The `Gptj` benchmark is a large-language model that does inference tasks.

The function currently is only implemented in one runtime, namely Python.


## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the `gptj-python` function.

### Invoke once
1. Start the function with docker-compose
   ```bash
   docker-compose -f ./yamls/docker-compose/dc-gptj-python.yaml up
   ```
2. In a new terminal, invoke the interface function with grpcurl.
   ```bash
   ./tools/bin/grpcurl -plaintext -d '{"regenerate": "false"}' localhost:50051 gptj.GptJBenchmark.GetBenchmark
   ```
    This will outputs the min, max and mean inference time of 1 inference, this may take around a few seconds. 
    Since inference of the gpt-j model may take awhile, we cache the latency info into a text file. If you want to regenerate the text file by doing another inference, change "false" to "true"
