module github.com/ease-lab/vSwarm/utils/tracing/go

go 1.16

require (
	github.com/containerd/containerd v1.6.2
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.31.0
	go.opentelemetry.io/otel v1.6.3
	go.opentelemetry.io/otel/exporters/zipkin v1.6.3
	go.opentelemetry.io/otel/sdk v1.6.3
	go.opentelemetry.io/otel/trace v1.6.3
	google.golang.org/grpc v1.45.0
)
