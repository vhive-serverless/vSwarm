# Image Rotate Benchmark

The image rotate benchmark rotates an input image by 90 degrees. An input image can be specified, but if nothing is given, a default image is used. This benchmark also utilises and depends on a database to store the images that can be used, which in turn uses MongoDB. 

The `init-database.go` script runs when starting the function and populates the database with the images from the `images` folder.

The functionality is implemented in two runtimes, namely Go and Python. The function is invoked using gRPC.

## Running this benchmark locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the image-rotate-python function.
1. Build or pull the function images using `make all-image` or `make pull`.
### Invoke once
2. Start the function with docker-compose
   ```bash
   docker-compose -f ./yamls/docker-compose/dc-image-rotate-python.yaml up
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

The detailed and general description on how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the image-rotate-python function.
1. Build or pull the function images using `make all-image` or `make pull`.
2. Initialise the database and start the function with knative
   ```bash
   kubectl apply -f ./yamls/knative/image-rotate-database.yaml
   kubectl apply -f ./yamls/knative/kn-image-rotate-python.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
### Invoke once
4. In a new terminal, invoke the interface function with test-client.
   ```bash
   ./test-client --addr $URL:80 --name "Example text for Image-rotate"
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