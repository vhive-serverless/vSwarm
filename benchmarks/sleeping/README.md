# Sleeping benchmark

The sleeping benchmark simulates a simple I/O bounded task by sleeping for 50 ms.

This benchmark can be used to verify that increasing in cpu frequency would not significantly affect the latency of I/O bounded workload.

The functionality is implemented in golang.

## Running this benchmark (using knative)

1. Build or pull the function images using `make all` or `make pull`.
2. Start the function with knative
   ```bash
   kn service apply -f ./yamls/knative/kn-sleeping-go.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
### Invoke once
4. In a new terminal, invoke the interface function with test-client.
   ```bash
   ./test-client --addr sleeping-go.default.192.168.1.240.sslip.io:80 --name "Example text for Sleeping"
   ```
### Invoke multiple times
4. Run the invoker
   ```bash
   # build the invoker binary
   cd ../../tools/invoker
   make invoker

   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "$URL" } ]' > endpoints.json

   # Start the invoker with a chosen RPS rate and time
   ./invoker -port 80 -dbg -time 10 -rps 1
   ```
## Tracing
This Benchmark supports distributed tracing for all runtimes. For the general use see vSwarm docs for tracing [locally](../../docs/running_locally.md#tracing) and with [knative](../../docs/running_benchmarks.md#tracing).