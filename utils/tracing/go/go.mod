module github.com/vhive-serverless/vSwarm/utils/tracing/go

go 1.16

require (
	github.com/containerd/containerd v1.6.8
	github.com/sirupsen/logrus v1.9.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.33.0
	go.opentelemetry.io/otel v1.11.1
	go.opentelemetry.io/otel/exporters/zipkin v1.11.1
	go.opentelemetry.io/otel/sdk v1.11.1
	go.opentelemetry.io/otel/trace v1.11.1
	google.golang.org/grpc v1.50.0
)
