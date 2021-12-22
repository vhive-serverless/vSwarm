# AES Benchmark

The AES benchmark use the AES128 algorithm to encrypt a certain message string.

The same functionality is implemented in different runtimes, namely Python, NodeJS and golang.



### Building images

###

## Running this benchmark

### Example aes-python

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it exemplary on the aes-python funtion.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with docker-compose
   ```
   docker-compose -f compose_yamls/docker-compose-aes-python.yaml up
   ```
3. In a new terminal, invoke the interface function with grpcurl. Since this function does not implement the reflection API we need to point `grpcurl` to use the helloworld protocol with `-import-path <path/to proto/dir> -proto helloworld.proto`.
   ```
   ../../tools/bin/grpcurl -plaintext -import-path proto -proto helloworld.proto localhost:50051 helloworld.Greeter.SayHello
   ```
4. Run the invoker
   ```
   # build the invoker binary
  cd ../../tools/invoker
  make invoker

  # Specify the hostname through "endpoints.json"
  echo '[ { "hostname": "localhost" } ]' > endpoints.json

  # Start the invoker with a chosen RPS rate and time
  ./invoker -port 50051 -dbg -time 10 -rps 1
   ```



### *getgid*-syscall

We instrumented each image with a *getgid()*-syscall. All syscalls can be traced using linux **perf**. With this we can easily see when the function is executed and how often. This was for development and will be removed most likely soon.