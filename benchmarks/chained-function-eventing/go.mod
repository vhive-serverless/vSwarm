module chained_function_eventing

go 1.21

replace github.com/vhive-serverless/vSwarm/tools/benchmarking_eventing => ../../tools/benchmarking_eventing

require (
	github.com/cloudevents/sdk-go/v2 v2.12.0
	github.com/kelseyhightower/envconfig v1.4.0
	github.com/vhive-serverless/vSwarm/tools/benchmarking_eventing v0.0.0-00010101000000-000000000000
	google.golang.org/grpc v1.61.1
	google.golang.org/protobuf v1.33.0
)

require (
	github.com/containerd/containerd v1.6.26 // indirect
	github.com/containerd/log v0.1.0 // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/google/uuid v1.4.0 // indirect
	github.com/json-iterator/go v1.1.12 // indirect
	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
	github.com/modern-go/reflect2 v1.0.2 // indirect
	github.com/sirupsen/logrus v1.9.3 // indirect
	go.uber.org/atomic v1.9.0 // indirect
	go.uber.org/multierr v1.8.0 // indirect
	go.uber.org/zap v1.21.0 // indirect
	golang.org/x/net v0.18.0 // indirect
	golang.org/x/sys v0.14.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20231106174013-bbf56f31fb17 // indirect
)
