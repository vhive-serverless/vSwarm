# Auth Benchmark

The auth benchmark ...

The same functionality is implemented in different runtimes, namely Python, NodeJS and golang.


## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the auth-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with docker-compose
   ```bash
   docker-compose -f compose_yamls/docker-compose-auth-python.yaml up
   ```
3. In a new terminal, invoke the interface function with grpcurl. To provide the helloworld protocol explicitly we'll use `-import-path <path/to proto/dir> -proto helloworld.proto`.
   ```bash
   ../../tools/bin/grpcurl -plaintext -import-path proto -proto helloworld.proto localhost:50051 helloworld.Greeter.SayHello
   ```
4. Run the invoker
   ```bash
   # build the invoker binary
   cd ../../tools/invoker
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "localhost" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 50051 -dbg -time 10 -rps 1
   ```


## Running this benchmark (using knative)

The detailed and general description how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the auth-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with knative
   ```bash
   kn service apply -f ./knative_yamls/auth-python.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
4. In a new terminal, invoke the interface function with grpcurl. To provide the helloworld protocol explicitly we'll use `-import-path <path/to proto/dir> -proto helloworld.proto`.
   ```bash
    ../../tools/bin/grpcurl -plaintext -import-path proto -proto helloworld.proto $URL:50051 helloworld.Greeter.SayHello
   ```
5. Run the invoker
   ```bash
   # build the invoker binary
   cd ../../tools/invoker
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "$URL" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 50051 -dbg -time 10 -rps 1
   ```
6. To use tracing, see [vSwarm docs here](../../docs/running_benchmarks.md#tracing)


### *getgid*-syscall

We instrumented each image with a *getgid()*-syscall. All syscalls can be traced using linux **perf**. With this we can easily see when the function is executed and how often. This was for development and will be removed most likely soon.
