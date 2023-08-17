# Hotel Reservation benchmarks

This folder contains 7 microservices from DeathStarBenchs [Hotel Reservation Application](https://github.com/delimitrou/DeathStarBench/tree/master/hotelReservation) ported as standalone serverless microbenchmarks.

### Background Hotel Reservation
The application implements a hotel reservation service, build with Go and gRPC, and starting from the open-source [Golang Microservices](https://github.com/harlow/go-micro-services) project.

The initial project was expended in DeathStarBench in several ways, including adding back-end in-memory and persistent databases, adding a recommender system for obtaining hotel recommendations, and adding the functionality to place a hotel reservation.

For functionality details refer to those two projects. [Golang Microservices](https://github.com/harlow/go-micro-services) and [Hotel Reservation Application](https://github.com/delimitrou/DeathStarBench/tree/master/hotelReservation).

#### Application Structure
![Screenshot 2021-08-25 070430](https://user-images.githubusercontent.com/31178749/130729727-94231cad-c6bb-4155-bb9b-0f622dfb553a.png)


## Porting to serverless
The app is broken down in the individual microservice to be able to run as standalone serverless micro kernel. Each of the function can be called directly using the specific gRPC protocol or via the [relay](../../tools/).

## Standalone functions benchmark summary

| Benchmark      | Knative infra | Dependent on        | Tracing | Runtimes        | Languages Implemented | gem5 support |
| -------------- | ------------- | ------------------- | :-----: | --------------- | --------------------- | :----------: |
| Geo            | Serving       | database            |    ✓    | docker, knative | Golang                |      ✓       |
| Profile        | Serving       | database, memcached |    ✓    | docker, knative | Golang                |      ✓       |
| Rate           | Serving       | database, memcached |    ✓    | docker, knative | Golang                |      ✓       |
| Recommendation | Serving       | database            |    ✓    | docker, knative | Golang                |      ✓       |
| Reservation    | Serving       | database, memcached |    ✓    | docker, knative | Golang                |      ✓       |
| User           | Serving       | database            |    ✓    | docker, knative | Golang                |      ✓       |
| Search         | Serving       | Geo, Profile, Rate  |    ✓    | docker, knative | Golang                |      ✕       |

## Running one of the benchmarks locally (using docker)

The detailed and general description how to run benchmarks local you can find [here](../../docs/running_locally.md). The following steps show it on the **geo** function.

### Starting the function container

1. Build or pull the function images using `make all-images` or `make pull`.
### Invoke once
2. Start the function with docker-compose
   ```bash
   docker-compose -f yamls/docker-compose/dc-geo.yaml up
   ```

This will start the geo function container together with the required database.
Furthermore it will start the relay container which provides the common interface to vSwarm's benchmarking tools. The port of the function container is exposed to 8083 the relay can be reached via port 50000.

### Invoking the function

#### Directly without relay
In a new terminal, invoke the interface function with grpcurl. You need use the [geo](https://github.com/vhive-serverless/vSwarm-proto/blob/main/proto/hotel_reserv/geo/geo.proto) protocol. The geo service implements the [reflection](https://github.com/fullstorydev/grpcurl#server-reflection) so you do not need to provide `grpcurl` with the proto file.

Call the Method _Nearby_ with latitude 37.7 and longitude -122.4
   ```bash
   ../../tools/bin/grpcurl -plaintext -d '{"lat":37.7,"lon":-122.4}' localhost:8083  geo.Geo.Nearby
   ```
#### With relay
In a new terminal, invoke the interface function with grpcurl.
   ```bash
   # Same steps, we just invoke the relay at port 50000 instead of geo server directly
   ../../tools/bin/grpcurl -plaintext -import-path tools/invoker/proto/ -proto helloworld.proto  localhost:50000 helloworld.Greeter.SayHello
   ```
### Invoke multiple times
2. Run the invoker
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

The detailed and general description how to run benchmarks on knative clusters you can find [here](../../docs/running_benchmarks.md). The following steps show it on the geo function.

1. Build or pull the function images using `make all-images` or `make pull`.

1. Deploy database.

   Geo depend on a database to be running. Deploy it first
   ```bash
   kubectl apply -f ./yamls/knative/database.yaml
   ```

1. Start the function with knative
   ```bash
   kubectl apply -f ./yamls/knative/kn-geo.yaml
   ```

1. **Note the URL provided in the output. The part without the `http://` we'll call `$URL`. Replace any instance of `$URL` in the code below with it.**

1. Run the invoker
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