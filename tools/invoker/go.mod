module github.com/vhive-serverless/vSwarm/tools/invoker

go 1.21

replace (
	github.com/vhive-serverless/vSwarm/tools/benchmarking_eventing => ../benchmarking_eventing
	github.com/vhive-serverless/vSwarm/tools/endpoint => ../endpoint
	github.com/vhive-serverless/vSwarm/tools/invoker/proto => ./proto
	github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go
)

require (
	github.com/containerd/containerd v1.7.6
	github.com/golang/protobuf v1.5.3
	github.com/google/uuid v1.4.0
	github.com/sirupsen/logrus v1.9.3
	github.com/vhive-serverless/vSwarm/tools/benchmarking_eventing v0.0.0-20231002141623-fe250ed33dde
	github.com/vhive-serverless/vSwarm/tools/endpoint v0.0.0-20231002141623-fe250ed33dde
	github.com/vhive-serverless/vSwarm/tools/invoker/proto v0.0.0-20231002141623-fe250ed33dde
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-20231002141623-fe250ed33dde
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.45.0
	google.golang.org/grpc v1.59.0
)

require (
	github.com/go-logr/logr v1.2.4 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/openzipkin/zipkin-go v0.4.2 // indirect
	go.opentelemetry.io/otel v1.19.0 // indirect
	go.opentelemetry.io/otel/exporters/zipkin v1.19.0 // indirect
	go.opentelemetry.io/otel/metric v1.19.0 // indirect
	go.opentelemetry.io/otel/sdk v1.19.0 // indirect
	go.opentelemetry.io/otel/trace v1.19.0 // indirect
	golang.org/x/net v0.15.0 // indirect
	golang.org/x/sys v0.12.0 // indirect
	golang.org/x/text v0.13.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20231002182017-d307bd883b97 // indirect
	google.golang.org/protobuf v1.31.0 // indirect
)
