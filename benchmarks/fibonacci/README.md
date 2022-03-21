# Fibonacci Benchmark

The Fibonacci benchmark runs the code to generate a fibonacci sequence. For more information on fibonacci sequence see [this](https://en.wikipedia.org/wiki/Fibonacci_number).

The same functionality is implemented in different runtimes, namely Python, NodeJS and golang.


## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the fibonacci-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with docker-compose
   ```bash
   docker-compose -f compose_yamls/docker-compose-fibonacci-python.yaml up
   ```
3. In a new terminal, invoke the interface function with grpcurl. To provide the helloworld protocol explicitly we'll use `-import-path <path/to proto/dir> -proto helloworld.proto`.
   ```bash
    ../../tools/bin/grpcurl -plaintext -import-path proto -proto helloworld.proto -d '{name: 12}' localhost:50051 helloworld.Greeter.SayHello
   ```
4. Modify the invoker.
    - `cd ../../tools/invoker`
    - Use `vi client.go` and edit `Name` field on Line 175 to a number of your choice.
5. Run the invoker
   ```bash
   # build the invoker binary
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "localhost" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 50051 -dbg -time 10 -rps 1
   ```

## Running this benchmark (using knative)

The detailed and general description how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the fibonacci-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with knative
   ```
   kn service apply -f ./knative_yamls/fibonacci-python.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
4. In a new terminal, invoke the interface function with grpcurl. To provide the helloworld protocol explicitly we'll use `-import-path <path/to proto/dir> -proto helloworld.proto`.
   ```bash
    ../../tools/bin/grpcurl -plaintext -import-path proto -proto helloworld.proto -d '{name: 12}' $URL:50051 helloworld.Greeter.SayHello
   ```
5. Modify the invoker.
    - `cd ../../tools/invoker`
    - Use `vi client.go` and edit `Name` field on Line 175 to a number of your choice.
6. Run the invoker
   ```bash
   # build the invoker binary
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "$URL" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 50051 -dbg -time 10 -rps 1
   ```
7. To use tracing, see [vSwarm docs here](../../docs/running_benchmarks.md#tracing)


### *getgid*-syscall

We instrumented each image with a *getgid()*-syscall. All syscalls can be traced using linux **perf**. With this we can easily see when the function is executed and how often. This was for development and will be removed most likely soon.
