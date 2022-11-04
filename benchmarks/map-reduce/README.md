# Map-Reduce

This benchmark implements a map-reduce process whereby a `Driver` function orchestrates
a number of `Mapper` instances which upload their results to an s3 bucket, after which point the
driver then calls a number of `Reducer` instances which read and reduce the values from the
previous mapper buckets into a final set of reduced buckets.

This benchmark relies on s3 for sharing input and output, and so inline transfer is not supported.

## Running this Benchmark using knative

1. First create a kubectl secret from your AWS Account's `AWS_ACCESS_KEY` and `AWS_SECRET_KEY`.
    These secrets will then be passed to the service in the knative manifests.
    There are [many ways](https://medium.com/avmconsulting-blog/secrets-management-in-kubernetes-378cbf8171d0) of creating the secret.
    Example:
    ```bash               
    export AWS_ACCESS_KEY=ABCDEFGHIJKLMNOPQRST
    export AWS_SECRET_KEY=ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMN
    kubectl create secret generic awscreds \
			--from-literal=awsaccess=${AWS_ACCESS_KEY} \
			--from-literal=awssecret=${AWS_SECRET_KEY}
    ```

2. Deploy the necessary functions using the `kn_deploy` script.
    ```bash
    ../../tools/kn_deploy.sh ./knative_yamls/s3/*
    ```
    Any sub-folder in the `knative_yamls` directory can be used, and all of the manifests therein
    must be deployed.

    `s3` contains manifests configured to use s3 for file transfer, with tracing disabled. The
    functions deployed using this set of manifests will have `TRANSFER_TYPE` set to `S3`.


3. Invoke the benchmark. The interface function of this benchmark is named `driver`. It can be
    invoked using the invoker or our test client, as described in the
    [running benchmarks](/docs/running_benchmarks.md) document.

## Instances
Number of instances per function in a stable flow:
| Function | Instances | Is Configurable |
|----------|-----------|-----------------|
| Driver | 1 | No |
| Mapper | 8 | Yes - Set `NUM_MAPPERS` in Driver and match scale in knative manifest. can't be more than 2215 |
| Reducer | 2 | Yes - Set `NUM_REDUCERS` in Driver and match scale in knative manifest. Must be power of 2 and smaller than `NUM_MAPPERS`|

## Parameters

### Flags

- `mAddr` - The address of the Mapper
- `rAddr` - The address of the Reducer
- `sp` - The port to which the driver will listen (which is used for invokation)
- `zipkin` - Address of the zipkin span collector

### Environment Variables

- `TRANSFER_TYPE` - The transfer type to use. Can be `INLINE` (default), `S3`, or `XDT`. Not
all benchmarks support all transfer types.
- `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGION` - Standard s3 keys, only needed if the s3
transfer type is used
- `ENABLE_TRACING` - Toggles tracing.
- `NUM_MAPPERS` - Sets the number of mappers to use. can't be more than 2215. Has to match the
number of instances of the mapper in knative, as defined with min/max scale settings in the manifest.
- `NUM_REDUCERS` - Sets the number of reducers to use. Must be power of 2 and smaller than
`NUM_MAPPERS`. Has to match the number of instances of the reducer in knative, as defined with
min/max scale settings in the manifest.
