# Online Shop Benchmarks

This folder contains 9 microservices from Googles [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) ported as standalone serverless microbenchmarks.

### Background
**Online Boutique** is a cloud-native microservices demo application.
It consists of a 10-tier microservices application. The application is a
web-based e-commerce app where users can browse items,
add them to the cart, and purchase them.

For functionality details refer to the upstream repository ([Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo)).


## Porting to serverless kernel
We took the 9 microservices implementing the functionality of the application and integrated them into vSwarm. The current version of the sources is **[v0.3.9](https://github.com/GoogleCloudPlatform/microservices-demo/releases/tag/v0.3.9)**.
> Note: To upgrade to another version see the `update_remote_files.sh` script.

> Warning: This is just a script for your convenience. No guarantee that everything will work afterwards.

## Functions summary

| Benchmark               | Knative infra | Tracing | Runtimes        | Languages Implemented | gem5 support | Description                                                                                                                       |
| ----------------------- | ------------- | :-----: | --------------- | --------------------- | :----------: | --------------------------------------------------------------------------------------------------------------------------------- |
| Cart Service            | Serving       |    ✕    | docker, knative | C#                    |      ✕       | Stores the items in the user's shopping cart in Redis and retrieves it.                                                           |
| Product Catalog Service | Serving       |    ✕    | docker, knative | Golang                |      ✓       | Provides the list of products from a JSON file and ability to search products and get individual products.                        |
| Currency Service        | Serving       |    ✕    | docker, knative | Node.js               |      ✓       | Converts one money amount to another currency. Uses real values fetched from European Central Bank. It's the highest QPS service. |
| Payment Service         | Serving       |    ✕    | docker, knative | Node.js               |      ✓       | Charges the given credit card info (mock) with the given amount and returns a transaction ID.                                     |
| Shipping Service        | Serving       |    ✕    | docker, knative | Golang                |      ✓       | Gives shipping cost estimates based on the shopping cart. Ships items to the given address (mock)                                 |
| Email Service           | Serving       |    ✕    | docker, knative | Python                |      ✓       | Sends users an order confirmation email (mock).                                                                                   |
| Checkout Service        | Serving       |    ✕    | docker, knative | Golang                |      ✕       | Retrieves user cart, prepares order and orchestrates the payment, shipping and the email notification.                            |
| Recommendation Service  | Serving       |    ✕    | docker, knative | Python                |      ✓       | Recommends other products based on what's given in the cart.                                                                      |
| Ad Service              | Serving       |    ✕    | docker, knative | Java                  |      ✕       | Provides text ads based on given context words.                                                                                   |

## Running one of the benchmarks locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the **adservice** function.

### Starting the function container

1. Build or pull the function images using `make all-images` or `make pull`.
### Invoke once
2. Start the function with docker-compose
   ```bash
   docker-compose -f yamls/docker-compose/dc-adservice.yaml up
   ```

This will start the adservice function container together with the relay container which provides the common interface to vSwarm's benchmarking tools. The port of the function container is exposed to 9555 the relay can be reached via port 50000.

### Invoking the function

#### With relay
In a new terminal, invoke the interface function with grpcurl.
   ```bash
   # Same steps, we just invoke the relay at port 50000 instead of geo server directly
   ../../tools/bin/grpcurl -plaintext -import-path tools/invoker/proto/ -proto helloworld.proto  localhost:50000 helloworld.Greeter.SayHello
   ```
### Invoke multiple times
Run the invoker with appropriate time and rps (requests per second)
   ```bash
   # build the invoker binary
   cd ../../tools/invoker
   make invoker
   # Specify the hostname through "endpoints.json"
   echo '[ { "hostname": "localhost" } ]' > endpoints.json
   # Start the invoker with a chosen RPS rate and time (With relay)
   ./invoker -port 50000 -dbg -time 10 -rps 1
   ```


## Running this benchmark (using knative)

The detailed and general description how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the adservice function.
1. Build or pull the function images using `make all-images` or `make pull`.
2. Start the function with knative
   ```bash
   kn service apply -f ./knative_yamls/kn-adservice.yaml
   ```
3. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**
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
We do not support tracing for this benchmark at the moment.