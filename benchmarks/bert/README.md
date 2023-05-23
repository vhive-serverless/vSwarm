# Bert Benchmark

The bert benchmark is a large-laguage model that does inference tasks.

The function currently is only implemented in one runtime, namely Python.


## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the bert-python function.
1. Download the data and model using `make setup`, this may take a lot of time
2. Build or pull the function images using `make all-images` or `make pull`.
### Invoke once
3. Start the function with docker-compose
   ```bash
   docker-compose -f ./yamls/docker-compose/dc-bert-python.yaml up
   ```
4. In a new terminal, invoke the interface function with grpcurl.
   ```bash
   ./tools/bin/grpcurl -plaintext localhost:50000 helloworld.Greeter.SayHello
   ```
    This will outputs the min, max and mean inference time of 100 inferences, this may take around 20 seconds.
