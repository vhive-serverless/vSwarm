# Map-Reduce

This benchmark implements a map-reduce process whereby a `Driver` function orchestrates
a number of `Mapper` instances which upload their results to an s3 bucket, after which point the 
driver then calls a number of `Reducer` instances which read and reduce the values from the
previous mapper buckets into a final set of reduced buckets.

This benchmark relies on s3 for sharing input and output, and so inline transfer is not supported.

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