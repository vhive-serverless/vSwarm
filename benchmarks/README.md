## Benchmark Summary

| Benchmark                     | Knative infra | tracing | s3   | Patterns | Num. of Unique Functions |
|-------------------------------|---------------|---------|------|----------|---|
| Chained Function Eventing     | Eventing      | ✕       | ✕    | pipeline | 2 |
| Chained Function Serving      | Serving       | ✓       | ✓    | pipeline | 2 |
| Map-Reduce                    | Serving       | ✓       | ✓    | scatter, gather | 3 |
| Corral (word count)           | Serving       | ✓       | ✕    | scatter, gather | 2 |
| Stacking-Training             | Serving       | ✓       | ✓    | broadcast, gather | 4 |
| Hyperparameter Tuning Halving | Serving       | ✓       | ✓    | broadcast, gather | 3 |
| Video Analytics               | Serving       | ✓       | ✓    | pipeline, scatter | 3 |
| Distributed compilation (gg)  | Serving       | ✕       | ✓    |   |   |
| Video decoding (gg)           | Serving       | ✕       | ✓    |   |   |

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