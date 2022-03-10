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


### Tracing

In benchmarks which support tracing (refer to [this summary](/benchmarks/README.md)), this can be
toggled by setting the `ENABLE_TRACING` environment variable to "true" or "false". This variable
should be included in every function, which prompts the function to emit traces which shall be
collected by a zipkin span collector.

Before deploying the functions, the zipkin span collector has to be set up. Many functions provide a separate docker-compose yaml file which will start the span collector and enable tracing appropriately.
> Note: For testing only single containers refer to the [zipkin](https://zipkin.io/pages/quickstart) documentation.

The above described workflow will only change in step 3 that you need to start the function with the tracing compose file
```
docker-compose -f <docker-compose manifest with '-tracing' filename> up
```
After step 5 you can inspect the traces by open your browser with `localhost:9411`
> Note if you work on a remote machine you need to froward port 9411. I.e. `ssh -i <path-to-key> -L 9411:127.0.0.1:9411 user@<IP>`

