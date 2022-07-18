module chained_function_eventing

go 1.16

replace github.com/ease-lab/vSwarm/tools/benchmarking_eventing => ../../tools/benchmarking_eventing

require (
	github.com/cloudevents/sdk-go/v2 v2.4.1
	github.com/ease-lab/vSwarm/tools/benchmarking_eventing v0.0.0-00010101000000-000000000000
	github.com/json-iterator/go v1.1.11 // indirect
	github.com/kelseyhightower/envconfig v1.4.0
	go.uber.org/atomic v1.9.0 // indirect
	go.uber.org/zap v1.17.0 // indirect
	google.golang.org/grpc v1.48.0
	google.golang.org/protobuf v1.28.0
)
