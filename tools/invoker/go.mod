module github.com/vhive-serverless/vSwarm/tools/invoker

go 1.21

replace (
	github.com/vhive-serverless/vSwarm/tools/benchmarking_eventing => ../benchmarking_eventing
	github.com/vhive-serverless/vSwarm/tools/endpoint => ../endpoint
	github.com/vhive-serverless/vSwarm/tools/invoker/proto => ./proto
	github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go
)

require (
	github.com/golang/protobuf v1.5.3
	github.com/google/uuid v1.5.0
	github.com/sirupsen/logrus v1.9.3
	github.com/vhive-serverless/vSwarm/tools/benchmarking_eventing v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/tools/endpoint v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/tools/invoker/proto v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-00010101000000-000000000000
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.46.1
	google.golang.org/grpc v1.60.1
)

require (
	github.com/containerd/containerd v1.6.26 // indirect
	github.com/containerd/log v0.1.0 // indirect
	github.com/go-logr/logr v1.3.0 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/openzipkin/zipkin-go v0.4.2 // indirect
	go.opentelemetry.io/otel v1.21.0 // indirect
	go.opentelemetry.io/otel/exporters/zipkin v1.21.0 // indirect
	go.opentelemetry.io/otel/metric v1.21.0 // indirect
	go.opentelemetry.io/otel/sdk v1.21.0 // indirect
	go.opentelemetry.io/otel/trace v1.21.0 // indirect
	golang.org/x/net v0.18.0 // indirect
	golang.org/x/sys v0.14.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20231002182017-d307bd883b97 // indirect
	google.golang.org/protobuf v1.31.0 // indirect
)
