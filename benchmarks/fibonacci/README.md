# Fibonacci Benchmark

The Fibonacci benchmark runs the code to generate a fibonacci sequence. For more information on fibonacci sequence see [the Wikipedia page](https://en.wikipedia.org/wiki/Fibonacci_number) for it.

The same functionality is implemented in different runtimes, namely Python, NodeJS and golang.


## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the fibonacci-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
### Invoke once
2. Start the function with docker-compose
   ```bash
   docker-compose -f ./yamls/docker-compose/dc-fibonacci-python.yaml up
   ```
3. In a new terminal, invoke the interface function with grpcurl.
   ```bash
   ./tools/bin/grpcurl -plaintext localhost:50000 helloworld.Greeter.SayHello
   ```
### Invoke multiple times
2. Run the invoker
   ```bash
   # build the invoker binary
   cd ../../tools/invoker
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "localhost" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time (With relay)
   ./invoker -port 50000 -dbg -time 10 -rps 1
   ```


## Running this benchmark (using knative)

The detailed and general description how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the fibonacci-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with knative
   ```bash
   kn service apply -f ./yamls/knative/kn-fibonacci-python.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
### Invoke once
4. In a new terminal, invoke the interface function with test-client.
   ```bash
   ./test-client --addr $URL:80 --name "Example text for Fibonacci"
   ```
### Invoke multiple times
4. Run the invoker
   ```bash
   # build the invoker binary
   cd ../../tools/invoker
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "$URL" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 80 -dbg -time 10 -rps 1
   ```
## Tracing
This Benchmark supports distributed tracing for all runtimes. For the general use see vSwarm docs for tracing [locally](../../docs/running_locally.md#tracing) and with [knative](../../docs/running_benchmarks.md#tracing).
