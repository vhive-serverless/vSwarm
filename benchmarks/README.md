## Benchmark Summary

| Benchmark                     | Knative infra | tracing | Transfer Types | Patterns | Num. of Unique Functions |
|-------------------------------|---------------|---------|----------------|----------|---|
| Chained Function Eventing     | Eventing      | ✕       | inline | pipeline | 2 |
| Chained Function Serving      | Serving       | ✓       | s3, inline  | pipeline, scatter, gather, broadcast | 3 |
| Map-Reduce                    | Serving       | ✓       | s3    | scatter, gather | 3 |
| Corral (word count)           | Serving       | ✓       | s3    | scatter, gather | 2 |
| Stacking-Training             | Serving       | ✓       | s3    | broadcast, gather | 4 |
| Hyperparameter Tuning Halving | Serving       | ✓       | s3    | broadcast, gather | 3 |
| Video Analytics               | Serving       | ✓       | s3, inline | pipeline, scatter | 3 |
| Distributed compilation (gg)  | Serving       | ✕       | s3    | scatter, gather | 1 |
| Video decoding (gg)           | Serving       | ✕       | s3    | scatter, gather | 1 |
| Fibonacci (gg)                | Serving       | ✕       | s3    | scatter, gather | 1 |

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

| Benchmark | Knative infra | tracing | Runtimes            | Languages implemented  |
|-----------|---------------|---------|---------------------|------------------------|
| AES       | Serving       | ✓       | docker, knative     | python, golang, nodejs |
| Auth      | Serving       | ✓       | docker, knative     | python, golang, nodejs |
| Fibonacci | Serving       | ✓       | docker, knative     | python, golang, nodejs |
