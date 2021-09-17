# Running Benchmarks

All of the benchmarks in the vSwarm benchmarking suite can be run on a Knative cluster. The majority of them can also
be run locally with docker-compose to test and demonstrate their functionality without serverless 
deployment. This document is concerned with running benchmarks with [vHive](https://github.com/ease-lab/vhive),
for instructions on testing benchmarks locally with docker-compose see the [running locally guide](./running_locally.md).

### Running Benchmarks on Knative Clusters

**You will need a vHive Knative cluster**. To set up a stock knative cluster see the vHive
[stock knative setup guide](https://github.com/ease-lab/vhive/blob/main/docs/developers_guide.md#testing-stock-knative-setup-or-images)
for a default knative cluster, or consider using the 
[vHive quickstart guide](https://github.com/ease-lab/vhive/blob/main/docs/quickstart_guide.md).

1. Deploy the benchmark functions as Knative services. The manifests for each benchmark function
    can be found in a sub-directory of the benchmark, e.g. 
    `/benchmarks/chained-function-serving/knative_yamls/inline/`.
    Follow the commands described in each benchmark folder to deploy any mix of functions.
     Benchmarks tend to have multiple
    sets of manifests which are used to deploy functions using different configurations, for
    example to toggle tracing or choosing which transfer type to use.
    ```bash
    ./tools/kn_deploy.sh ./benchmarks/path/to/manifests/*
    ```
    The function deployment can be monitored using `kn service list --all` 
    > **Note:**
    > 
    > Deployment of Knative Eventing benchmarks requires more steps, so such benchmarks will
    > have an `apply.sh` script in the manifests folder.
    >
    > This deployment script substitutes necessary environment variables into the knative manifests.
    > This includes variables such as AWS keys. For more detail see the 
    > [file transfer](#file-transfer) section.

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

    *Alternatively*, the test client can be used to invoke the benchmark. This is a bare-bones
    client which invokes the function at the given address with a helloworld grpc message, similar
    to how one might use grpcurl, however it is compatible with more manifest configurations.
    ```bash
    cd ./tools/test-client
    go build ./test-client.go
    ./test-client -addr <HOSTNAME>:<PORT>
    ```

3. If needed, the logs of individual functions can be checked using `kubectl logs`:
    ```bash
    # find the name of the pod
    kubectl get pods -A

    # view the logs of the pod
    kubectl logs <POD_NAME> -c user-container
    ```

### Tracing

In benchmarks which support tracing (refer to [this summary](/benchmarks/README.md)), this can be
toggled by setting the `ENABLE_TRACING` environment variable to "true" or "false". This variable
should be included in every function, which prompts the function to emit traces which shall be
collected by a zipkin span collector.

Before deploying the functions, the zipkin span collector has to be set up. In vHive the
[`setup_zipkin.sh`](https://github.com/ease-lab/vhive/blob/main/scripts/setup_zipkin.sh) script can
be used to do this. Refer to the [knative tracing](https://github.com/ease-lab/vhive/blob/main/docs/developers_guide.md#knative-request-tracing)
section of the vHive developers guide for further information.

Once the span collector is deployed, the benchmark functions can be deployed as normal.

### Debugging

Most of the workloads in vSwarm support docker-compose, which enables the functionality of the
benchmark to be tested outside of the knative cluster. Please see the end-to-end CI files for any
one of these benchmarks for an example of how docker-compose can be run.

Logs for functions running inside knative can also be accessed to help with debugging, as is done
in our end-to-end CI. Example:
```bash
kubectl logs -n default -c user-container -l serving.knative.dev/service=gg-driver-llvm --tail=-1
```
If a pod experiences an error and has to restart, the old logs can still be accessed by adding
`-p` to the above command.

Outside of the CI, when running a benchmark by hand, it can be very useful to "enter" the function
 pod by using its bash console, letting you run scripts manually or check the contents or access 
 permissions of files, and so on. For example:
```bash
kubectl exec -it -c user-container <POD NAME> -- /bin/sh
```

## File Transfer

When transferring files - or any other payload or message - either inline or external transfer could
be used. Inline transfer sends the payload over http, via the load balancer within knative. With
external transfer a service such as `s3` can be used, where one function uploads data to an agreed
s3 bucket, and another pulls data from this bucket when prompted. Most benchmarks in vSwarm
support both inline and s3 transfer, but sometimes only one or the other is supported. 

If inline transfer is used, no additional flags or environment variables need to be passed or set, 
typically making this the simplest form of transfer. If s3 is used, though, then some additional
parameters must be set. 

Connecting to s3 requires an access key and a secret key, such that the function can access the 
shared bucket. All the functions in this suite look for these parameters in the `AWS_ACCESS_KEY` 
and `AWS_SECRET_KEY` environment variables. Additionally the `AWS_REGION` sometimes needs to be
set to specify the region. Additionally, the functions typically assume that the target bucket
already exists on s3, so if a new s3 instance is being used then these buckets may need to be
created on s3 manually.

The transfer type used, be it "inline", "s3", or something else, can be set in the 
`TRANSFER_TYPE` environment variable. If left unset, most functions default to inline transfer.