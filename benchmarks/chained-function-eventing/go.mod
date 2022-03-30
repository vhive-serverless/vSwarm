module chained_function_eventing

go 1.16

replace github.com/ease-lab/vSwarm/tools/benchmarking_eventing => ../../tools/benchmarking_eventing

require (
	github.com/cloudevents/sdk-go/v2 v2.8.0
	github.com/ease-lab/vSwarm/tools/benchmarking_eventing v0.0.0-00010101000000-000000000000
	github.com/kelseyhightower/envconfig v1.4.0
	google.golang.org/grpc v1.45.0
	google.golang.org/protobuf v1.28.0
)
