# Running Benchmarks Locally

Most benchmarks can be run locally using docker-compose for testing purposes.

You will need `Docker` and `docker-compose`. Note that a few benchmarks which use Knative Eventing
can't be without Knative and don't support local execution with docker-compose.

Some benchmarks use XDT, which will require that the `GOPRIVATE_KEY` environment variable is set
to access the private XDT repository. Some benchmarks will also require access to AWS S3 services
for file transfer, this requires the `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` environment variables.
Contact us if you would like to ask for our keys, or see the [File Transfer](./running_benchmarks.md#file-transfer)
section for more information.

1. `cd` to the benchmark's directory, e.g.
   [`./benchmarks/chained-function-serving/`](/benchmarks/chained-function-serving/).
2. Make docker images locally with `make all-image`.

   > **Note:**
   >
   > Most benchmarks will require the `GOPRIVATE_KEY` environment variable to be built. If you
   > do not have access to our key yet you can usually skip this step and docker-compose should
   > pull our pre-built image from docker hub in the next step.

3. Start the benchmark with docker-compose. Most benchmarks have a number of docker-compose
   manifests, only one can be chosen. These are used to enable different features, for example
   `docker-compose-s3.yml` or `docker-compose-inline.yml` for choosing between which transfer
   type to use.

   ```bash
   docker-compose -f <docker-compose manifest filename> up
   ```

   > **Note:**
   >
   > If s3 is used then the necessary environment variables, `AWS_ACCESS_KEY` and `AWS_SECRET_KEY`
   > need to be set. see [File Transfer](./running_benchmarks.md#file-transfer) for more details.
   > If you currently don't have access to s3 then you will only be able to run `-inline`
   > manifests

4. In a new terminal, invoke the interface function with grpcurl. We have included the grpcurl
   binary in this repository:

   ```bash
   ../../tools/bin/grpcurl -plaintext localhost:50051 helloworld.Greeter.SayHello
   ```

   Depending on the benchmark, this might take a moment to complete. You can track the logs in
   the first terminal window to monitor the benchmark progress.

   > **Note:**
   >
   > All of our docker-compose manifests are configured to expose port 50051, and all interface
   > functions implement the `helloworld.Greeter.SayHello` rpc service. In rare cases additional
   > data must be passed to the function using the `-d` flag- this will be stated explicitly
   > in the README of that particular benchmark.

5. (Optionally) You can also invoke the benchmark using the invoker. `golang` will be required to
   build the invoker binary. Find out more about the invoker [here](/tools/invoker/).

   ```bash
   # build the invoker binary
   cd ../../tools/invoker
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "localhost" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 50051 -dbg -time 60 -rps 0.0667
   ```
