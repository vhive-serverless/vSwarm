## Benchmark Summary

| Benchmark                     | Knative infra | tracing | s3   | Patterns |
|-------------------------------|---------------|---------|------|----------|
| Chained Function Eventing     | Eventing      | ✕       | ✕    | pipeline |
| Chained Function Serving      | Serving       | ✓       | ✓    | pipeline |
| Map-Reduce                    | Serving       | ✓       | ✓    | scatter, gather |
| Corral (word count)           | Serving       | ✓       | ✕    | scatter, gather |
| Stacking-Training             | Serving       | ✓       | ✓    | broadcast, gather |
| Hyperparameter Tuning Halving | Serving       | ✓       | ✓    | broadcast, gather |
| Video Analytics               | Serving       | ✓       | ✓    | pipeline, scatter |
| Distributed compilation (gg)  | Serving       | ✕       | ✓    |   |
| Video decoding (gg)           | Serving       | ✕       | ✓    |   |