# Corral Benchmark

This benchmark uses the [Corral MapReduce framework](https://github.com/bcongdon/corral):

Corral is a MapReduce framework designed to be deployed to serverless platforms, like 
[AWS Lambda](https://aws.amazon.com/lambda/). It presents a lightweight alternative to Hadoop 
MapReduce. Much of the design philosophy was inspired by Yelp's mrjob -- corral retains mrjob's ease-of-use while gaining the 
type safety and speed of Go.

## Running this Benchmark

1. Make sure to set the `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` environment variables.
    The kn_deploy script will then substitute these values into the knative manifests.
    Example:
    ```bash               
    export AWS_ACCESS_KEY=ABCDEFGHIJKLMNOPQRST
    export AWS_SECRET_KEY=ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMN
    ```

2. Deploy the necessary functions using the `kn_deploy` script.
    ```bash
    ../../tools/kn_deploy.sh ./knative_yamls/*
    ```
    Only one set of manifests is provided by default for this benchmark. Both of the manifests in
    the `knative_yamls` folder must be deployed. These default manifests deploy functions with
    the `s3` transfer type enabled, and with tracing turned off.

3. Invoke the benchmark. The interface function of this benchmark is named `word-count-driver`. It can be
    invoked using the invoker or our test client, as described in the 
    [running benchmarks](/docs/running_benchmarks.md) document.

## Instances
Number of instances per function in a stable flow:
| Function | Instances | Is Configurable |
|----------|-----------|-----------------|
| Driver | 1 | No |
| Worker | 1 | No |

## Parameters

### Environment Variables

- `TRANSFER_TYPE` - The transfer type to use. Can be `INLINE` (default), `S3`, or `XDT`. Not
all benchmarks support all transfer types.
- `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGION` - Standard s3 keys, only needed if the s3
transfer type is used
- `ENABLE_TRACING` - Toggles tracing - Not supported by this benchmark
- `PORT` - Specifies the port which the driver listens to.
- `CORRAL_DRIVER` - Used to toggle between driver and worker functionality during function setup.

## Benchmark Results

| Benchmark      | Job Execution Time |
|----------------|--------------------|
| test_wc_local  | 170ms              |
| test_wc_s3     | 3.79sec            |
| test_wc_lambda | 3.92sec            |
