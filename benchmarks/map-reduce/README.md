# Map-Reduce



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