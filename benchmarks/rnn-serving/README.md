# RNN Serving Benchmark

The RNN serving benchmark generates a string using an RNN model given a specific language to generate the string in. An language can be specified as an input, but if nothing is given, a default language is chosen, either at random or uniquely using the input generator.  

The functionality is implemented in Python. The function is invoked using gRPC.

## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the rnn-serving-python function.
1. Build or pull the function images using `make all-image` or `make pull`.
### Invoke once
2. Start the function with docker-compose
   ```bash
   docker-compose -f ./yamls/docker-compose/dc-rnn-serving-python.yaml up
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

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 50000 -dbg -time 10 -rps 1
   ```

## Running this benchmark (using knative)

The detailed and general description on how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the rnn-serving-python function.
1. Build or pull the function images using `make all-image` or `make pull`.
2. Initialise the database and start the function with knative
   ```bash
   kubectl apply -f ./yamls/knative/kn-rnn-serving-python.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
### Invoke once
4. In a new terminal, invoke the interface function with test-client.
   ```bash
   ./test-client --addr $URL:80 --name "Example text for rnn-serving"
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

This Benchmark does not support distributed tracing for now.