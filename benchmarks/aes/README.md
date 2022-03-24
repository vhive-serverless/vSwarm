# AES Benchmark

The AES benchmark use the AES128 algorithm to encrypt a certain message string. As we are using the helloworld gRPC protocol for this benchmark the message will be the `name` variable. If you do not specify a name a default name is taken. You can change the default name with the argument `default-plaintext`.

AES requires a secrete key for encryption. The functions use a default key but you can specify your own by passing it with the `key` argument to the function. See source code for more details.

The same functionality is implemented in different runtimes, namely Python, NodeJS and golang.





## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the aes-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with docker-compose
   ```bash
   docker-compose -f yamls/docker-compose/dc-aes-<runtime>.yaml up
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

The detailed and general description how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the aes-python function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with knative
   ```bash
   kn service apply -f ./knative_yamls/aes-python.yaml
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
## Tracing
This Benchmark supports distributed tracing for all runtimes. For the general use see vSwarm docs for tracing [locally](../../docs/running_locally.md#tracing) and with [knative](../../docs/running_benchmarks.md#tracing).
