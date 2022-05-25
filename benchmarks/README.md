# Benchmark summary

vSwarm currently supports two kinds of microbenchmarks. One is the **multi-function benchmark**, which involves synchronous and asynchronous function composition. The other is **standalone function benchmark** where each function is a single function and not a composition of multiple functions (i.e. no producer-consumer functions).

## Multi-function benchmark Summary

| Benchmark                     | Knative infra | tracing | Transfer Types | Patterns                             | Num. of Unique Functions |
| ----------------------------- | ------------- | ------- | -------------- | ------------------------------------ | ------------------------ |
| Chained Function Eventing     | Eventing      | ✕       | inline         | pipeline                             | 2                        |
| Chained Function Serving      | Serving       | ✓       | s3, inline     | pipeline, scatter, gather, broadcast | 3                        |
| Map-Reduce                    | Serving       | ✓       | s3             | scatter, gather                      | 3                        |
| Corral (word count)           | Serving       | ✓       | s3             | scatter, gather                      | 2                        |
| Stacking-Training             | Serving       | ✓       | s3             | broadcast, gather                    | 4                        |
| Hyperparameter Tuning Halving | Serving       | ✓       | s3             | broadcast, gather                    | 3                        |
| Video Analytics               | Serving       | ✓       | s3, inline     | pipeline, scatter                    | 3                        |
| Distributed compilation (gg)  | Serving       | ✕       | s3             | scatter, gather                      | 1                        |
| Video decoding (gg)           | Serving       | ✕       | s3             | scatter, gather                      | 1                        |
| Fibonacci (gg)                | Serving       | ✕       | s3             | scatter, gather                      | 1                        |

## Patterns

- **Pipeline** - Describes a 1-to-1 workflow from one function to another, such that a chain of
functions are used to execute the benchmark.
- **Broadcast** - Describes a pattern whereby one function sends the same payload to multiple
recipient functions and awaits their individual replies, similar to publisher-subscriber design
pattern. A common example can be seen in distributed ML training where the same training model is
passed to multiple consumers.
- **Scatter** - Describes a fan-out one-to-many pattern whereby one function sends payloads to
multiple recipients. Unlike the broadcast pattern, the sent payloads are different from each other.
- **Gather** - Describes a fan-in many-to-one pattern, whereby a consumer retrieves objects from
multiple producers, e.g., as in the reduce phase in MapReduce.


## Standalone functions benchmark summary

| Benchmark | Knative infra | Tracing | Runtimes        | Languages Implemented  | gem5 support |
| --------- | ------------- | :-----: | --------------- | ---------------------- | :----------: |
| AES       | Serving       |    ✓    | docker, knative | Python, Golang, Nodejs |      ✓       |
| Auth      | Serving       |    ✓    | docker, knative | Python, Golang, Nodejs |      ✓       |
| Fibonacci | Serving       |    ✓    | docker, knative | Python, Golang, Nodejs |      ✓       |

**Online shop**
| Benchmark               | Knative infra | Tracing | Runtimes        | Languages Implemented | gem5 support |
| ----------------------- | ------------- | :-----: | --------------- | --------------------- | :----------: |
| Cart Service            | Serving       |    ✕    | docker, knative | C#                    |      ✕       |
| Product Catalog Service | Serving       |    ✕    | docker, knative | Golang                |      ✓       |
| Currency Service        | Serving       |    ✕    | docker, knative | Node.js               |      ✓       |
| Payment Service         | Serving       |    ✕    | docker, knative | Node.js               |      ✓       |
| Shipping Service        | Serving       |    ✕    | docker, knative | Golang                |      ✓       |
| Email Service           | Serving       |    ✕    | docker, knative | Python                |      ✓       |
| Checkout Service        | Serving       |    ✕    | docker, knative | Golang                |      ✕       |
| Recommendation Service  | Serving       |    ✕    | docker, knative | Python                |      ✓       |
| Ad Service              | Serving       |    ✕    | docker, knative | Java                  |      ✕       |

**Hotel App**
| Benchmark      | Knative infra | Tracing | Runtimes        | Languages Implemented | gem5 support |
| -------------- | ------------- | :-----: | --------------- | --------------------- | :----------: |
| Geo            | Serving       |    ✓    | docker, knative | Golang                |      ✓       |
| Profile        | Serving       |    ✓    | docker, knative | Golang                |      ✓       |
| Rate           | Serving       |    ✓    | docker, knative | Golang                |      ✓       |
| Recommendation | Serving       |    ✓    | docker, knative | Golang                |      ✓       |
| Reservation    | Serving       |    ✓    | docker, knative | Golang                |      ✓       |
| User           | Serving       |    ✓    | docker, knative | Golang                |      ✓       |
| Search         | Serving       |    ✓    | docker, knative | Golang                |      ✕       |
