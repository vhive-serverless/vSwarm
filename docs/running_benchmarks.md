# Running Benchmarks

All of the benchmarks in this suite can be run on a Knative cluster. The majority of them can also
be run locally with docker-compose to test and demonstrate their functionality without serverless 
deployment.

### Running Benchmarks Locally
You will need `Docker` and `docker-compose`. Note that a few benchmarks which use Knative Eventing 
can't be without Knative and don't support local execution with docker-compose.

Some benchmarks use XDT, which will require that the `GOPRIVATE_KEY` environment variable is set
to access the private XDT repository. Some benchmarks will also require access to AWS S3 services
for file transfer, this requires the `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` environment variables.
Contact us if you would like to ask for our keys, or see the [File Transfer](#file-transfer) 
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
    > need to be set. see [File Transfer](#file-transfer) for more details.
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

### Running Benchmarks on Knative Clusters
You will need a Knative cluster. If you would like to make a cluster, we recommend using 
[vHive](https://github.com/ease-lab/vhive) for a quick and easy startup: You can follow the
[stock knative setup guide](https://github.com/ease-lab/vhive/blob/main/docs/developers_guide.md#testing-stock-knative-setup-or-images)
for a default knative cluster, or consider using the 
[vHive quickstart guide](https://github.com/ease-lab/vhive/blob/main/docs/quickstart_guide.md).

1. Deploy the benchmark functions as Knative services. The manifests for each benchmark function
    can be found in a sub-directory of the benchmark, e.g. 
    `/benchmarks/chained-function-serving/knative_yamls/inline/`. Benchmarks tend to have multiple
    sets of manifests which are used to deploy functions using different configurations, similar to
    how there are multiple docker-compose manifests.
    ```bash
    ./tools/kn_deploy.sh ./benchmarks/path/to/manifests/*
    ```
    The function deployment can be monitored using `kn service list --all` 
    > **Note:**
    > 
    > Deployment of Knative Eventing benchmarks requires more steps, so such benchmarks will
    > have an `apply.sh` script in the manifests folder.

2. Invoke the benchmark via the interface function. Like with docker-compose, the interface
    function always implements the `helloworld.Greeter.SayHello` rpc service. We recommend using
    the `invoker` over using `grpcurl` since some function manifests include configurations that
    interfere with grpcurl.

    The hostname of the interface function can be double-checked with `kn service list --all`, for
    example: "driver.default.127.0.0.1.nip.io". Do not include the "http://" protocol prefix. The
    interface function can have a different name depending on the benchmark, this is documented
    in the README within each benchmark's directory.
    ```bash
    # build the invoker binary
    cd ./tools/invoker
    make invoker

    # Specify the hostname through "endpoints.json"
    echo '[ { "hostname": "<YOUR_HOSTNAME>" } ]' > endpoints.json

    # Start the invoker with a chosen RPS rate and time
    ./invoker -port 80 -dbg -time 60 -rps 0.016667
    ``` 

3. If needed, the logs of individual functions can be checked using `kubectl logs`:
    ```bash
    # find the name of the pod
    kubectl get pods -A

    # view the logs of the pod
    kubectl logs <POD_NAME> -c user-container
    ```

## File Transfer

When transfering files - or any other payload or message - either inline or external transfer could
be used. Inline transfer sends the payload over http, via the load balancer within knative. With
external transfer a service such as `s3` can be used, where one function uploads data to an agreed
s3 bucket, and another pulls data from this bucket when prompted. Most benchmarks in this suite 
support both inline and s3 transfer, but sometimes only one or the other is supported. 

If inline transfer is used, no additional flags or environment variables need to be passed or set, 
typically making this the simplest form of transfer. If s3 is used, though, then some additional
paramaters must be set. 

Connecting to s3 requires an access key and a secret key, such that the function can access the 
shared bucket. All the functions in this suite look for these paramaters in the `AWS_ACCESS_KEY` 
and `AWS_SECRET_KEY` environment variables. Additionally the `AWS_REGION` sometimes needs to be
set to specify the region. Additionally, the functions typically assume that the target bucket
already exists on s3, so if a new s3 instance is being used then these buckets may need to be
created on s3 manually.

The transfer type used, be it "inline", "s3", or something else, can be set in the 
`TRANSFER_TYPE` environment variable. If left unset, most functions default to inline transfer.