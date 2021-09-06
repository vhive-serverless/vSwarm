# Chained Function Serving
![diagram](diagram.png)

This is a basic example benchmark demonstrating how multiple functions can be chained together
using knative serving. The benchmark consists of two functions, **Producer** and **Consumer*,
which are used to imitate the producer-consumer design pattern whereby the prior creates some
object and sends it to the latter, where it is "consumed".

The consumer is a server which listens on a set port. Upon receiving a call from the producer it
logs the value that was sent to it, and return an acknowledgement. The producer is a client which
connects to the consumer, sends it a payload, and await acknowledgement. The producer is also
simultaneously a server which we, as the user, can call in order to trigger the payload being sent.

From the control flow perspective, we invoke the producer first, which then sends its payload to
the consumer. Subsequently the consumer shall reply to the producer, which then replies to us.

The producer is the interface function, implementing the standard helloworld grpc service. The
producer and consumer use a separate "ProducerConsumer" grpc service for sending the payload
and recieving the acknowledgement.

## Parameters

### Flags

- `addr` - The address of the consumer
- `pc` - The port on which the consumer is listening
- `ps` - The port to which the producer will listen (which is used for invokation)
- `zipkin` - Address of the zipkin span collector
- `transferSize` -  Number of KBs to transfer to the consumer

### Environment Variables

- `TRANSFER_TYPE` - The transfer type to use. Can be `INLINE` (default), `S3`, or `XDT`. Not
all benchmarks support all transfer types.
- `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGION` - Standard s3 keys, only needed if the s3
transfer type is used
- `ENABLE_TRACING` - Toggles tracing.