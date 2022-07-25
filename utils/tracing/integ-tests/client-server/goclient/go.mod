module tests/tracing/python/client-server

go 1.16

require (
	github.com/containerd/containerd v1.6.6
	github.com/ease-lab/vSwarm-proto v0.2.0
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-20220719164711-8782cc0ff194
	github.com/sirupsen/logrus v1.9.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.33.0
	go.opentelemetry.io/otel/exporters/zipkin v1.8.0 // indirect
	golang.org/x/net v0.0.0-20220722155237-a158d28d115b // indirect
	golang.org/x/sys v0.0.0-20220722155257-8c9f86f7a55f // indirect
	google.golang.org/genproto v0.0.0-20220722212130-b98a9ff5e252 // indirect
	google.golang.org/grpc v1.48.0
)
