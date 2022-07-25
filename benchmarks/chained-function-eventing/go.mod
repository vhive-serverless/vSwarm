module chained_function_eventing

go 1.16

replace github.com/ease-lab/vSwarm/tools/benchmarking_eventing => ../../tools/benchmarking_eventing

require (
	github.com/cloudevents/sdk-go/v2 v2.10.1
	github.com/ease-lab/vSwarm/tools/benchmarking_eventing v0.0.0-20220719164711-8782cc0ff194
	github.com/kelseyhightower/envconfig v1.4.0
	google.golang.org/grpc v1.48.0
	google.golang.org/protobuf v1.28.0
)
