# Chained Function Serving
![diagram](diagram.png)

This is an example benchmark demonstrating how multiple functions can be chained together
using knative serving. The core of the benchmark consists of two functions, **Producer** and 
**Consumer**, which are used to imitate the producer-consumer design pattern whereby the prior
creates some object and sends it to the latter, where it is "consumed".

The consumer is a server which listens on a set port. Upon receiving a call from the producer it
logs the value that was sent to it, and return an acknowledgement. The producer is a client which
connects to the consumer, sends it a payload, and await acknowledgement. The producer is also
simultaneously a server which we, as the user, can call in order to trigger the payload being sent.

From the control flow perspective, we invoke the producer first, which then sends its payload to
the consumer. Subsequently the consumer shall reply to the producer, which then replies to us.

There is also a third function, the **Driver**, which allows us to benchmark gather, scatter, and
broadcast patterns in addition to the basic pipeline pattern as described above.

In a gather (`fan-in`) experiment the driver will invoke multiple producers which each produce a 
"capability". The driver then invokes one consumer which receives the list of capabilities and 
consumes them, thereby we have one function "gather" payloads from multiple other functions.

In a scatter (`fan-out`) experiment the driver invokes a single producer which goes on to send
payloads to multiple consumers. The broadcast experiment is similar, but the payload (capability)
is only uploaded once and the same key is sent to all consumers, whereas in scatter experiments
the producer uploads a separate payload for each consumer and hence each consumer receives a unique
reference key. 

Due to the way in which keys must be shared and capabilities uploaded in gather, scatter, and
broadcast experiments, these configurations of the benchmark only support `s3` transfer. The
basic pipeline configuration (which does not require the use of a driver) also supports the
`inline` transfer type.

## Running this Benchmark

1. If s3 is used, make sure to set the `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` environment variables!
    The kn_deploy script will then substitute these values into the knative manifests.
    Example:
    ```bash               
    export AWS_ACCESS_KEY=ABCDEFGHIJKLMNOPQRST
    export AWS_SECRET_KEY=ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMN
    ```

2. Deploy the necessary functions using the `kn_deploy` script.
    ```bash
    ../../tools/kn_deploy.sh ./knative/s3/*
    ```
    Any sub-folder in the `knative_yamls` directory can be used, and all of the manifests therein
    must be deployed.

    The sub-folders each contain an example configuration, and the can differ by the transfer type
    used as well as the configuration used. Please see the [instances](#instances) section of this
    document for further explanation of the different configurations available for this benchmark.

    `fanin-basic` and `fanout-basic` contain manifests for the fan-in and fan-out configuration
    respectively. They both use the s3 transfer type and have tracing disabled.

    `inline` contains the most generic example of this benchmark, which is a pipeline configuration
    using the inline transfer type and with tracing disabled.

    `s3` contains another fan-in s3 configuration, also with tracing disabled. The fan-in degree
    and transfer size in this configuration differ from the `fanin-basic` configuration.
    

3. Invoke the benchmark. The interface function of this benchmark depends on which configuration is
    has been deployed: `producer` should be used in the `pipeline` configuration, and `driver` in
    all other cases. The appropriate function should be invoked using the invoker or our test 
    client, as described in the [running benchmarks](/docs/running_benchmarks.md) document.

## Instances
Number of instances per function in a stable flow:
| Function | Instances | Is Configurable |
|----------|-----------|-----------------|
| Driver | 1 | No |
| Producer | N | Yes |
| Consumer | N | Yes |

This benchmark is highly configurable, enabling the benchmarking of 4 distinct patterns, however
each pattern must be configured in a very specific way which requires additional explanation:

### Pipeline

This is the basic pattern involving just one producer and one consumer. No driver is needed. The
manifests for the producer and consumer should use just one instance, and the `FANIN` and `FANOUT`
environment variables should both be set to zero. The producer can be invoked directly with the
standard `helloworld` grpc call.

### Gather

All three functions are required for this pattern. There should be one driver and one consumer
instance, and the desired number (`N`) of producer instances defined in their respective
manifests, where `N` is the fan-in degree. `FANOUT` should be set to 0, and `FANIN` should be set 
to `N` in each function. The benchmark is started by invoking the driver.

### Scatter

All three functions are used in this pattern. There should be one driver and one producer, and
the desired number (`N`) of consumers defined in their appropriate manifests, where `N` is the 
fan-out degree. `FANOUT` should be set to the fan-out degree, `N`, and `FANIN` to 0. The driver is
the also interface function for this configuration.

### Broadcast

This has a very similar setup to the scatter pattern. Only one driver and producer instance are
needed, and `N` consumers. `FANIN` and `FANOUT` are both set to 0, and the `BROADCAST` environment
variable is set to `N`.

## Parameters

### Flags

- `addr` - The address of the consumer (in the producer function)
- `pc` - The port on which the consumer is listening
- `ps` - The port to which the producer will listen (which is used for invokation)
- `zipkin` - Address of the zipkin span collector
- `transferSize` -  Number of KBs to transfer to the consumer
- `prodEndpoint` - Address of the producer (in the Driver)
- `consEndpoint` - Address of the consumer (in the Driver)

### Environment Variables

- `TRANSFER_TYPE` - The transfer type to use. Can be `INLINE` (default), `S3`, or `XDT`. Not
all benchmarks support all transfer types.
- `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGION` - Standard s3 keys, only needed if the s3
transfer type is used
- `ENABLE_TRACING` - Toggles tracing.
- `FANIN`, `FANOUT`, `BROADCAST` - used to set the benchmark configuration for a specific pattern.
Refer to the [Instances section](#instances).