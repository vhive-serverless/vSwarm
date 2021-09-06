# Hyperparameter Tuning Halving
![diagram](diagram.png)

This benchmark implements iterative RandomForest training. It consists of a **Driver** function
which manages multiple training models, and a **Trainer** function used for training individual
models. The driver is the interface function implementing the standard helloworld grpc service, and
its job is to iteratively train a number of models until the best model is found.

Each iteration, the driver uses a subset of the dataset to train a number of models by issuing
requests to the training function. After training, only the top 50% of models are kept for the next
iteration, and the size of the dataset subset used for training is increased 
accordingly. This is
repeated until only one model remains.

This benchmark relies on s3 for sharing models between driver and trainer.

## Parameters

### Flags

- `tAddr` - The address of the Trainer
- `sp` - The port to which the driver will listen (which is used for invokation)
- `zipkin` - Address of the zipkin span collector

### Environment Variables

- `TRANSFER_TYPE` - The transfer type to use. Can be `INLINE` (default), `S3`, or `XDT`. Not
all benchmarks support all transfer types.
- `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGION` - Standard s3 keys, only needed if the s3
transfer type is used
- `ENABLE_TRACING` - Toggles tracing.