module github.com/ease-lab/vSwarm/utils/tracing/go

go 1.16

require (
	github.com/containerd/containerd v1.6.2
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.31.0
	go.opentelemetry.io/otel v1.8.0
	go.opentelemetry.io/otel/exporters/zipkin v1.8.0
	go.opentelemetry.io/otel/sdk v1.8.0
	go.opentelemetry.io/otel/trace v1.8.0
	google.golang.org/grpc v1.47.0
)

require (
	cloud.google.com/go v0.99.0 // indirect
	golang.org/x/net v0.0.0-20220425223048-2871e0cb64e4 // indirect
	golang.org/x/sys v0.0.0-20220412211240-33da011f77ad // indirect
	google.golang.org/genproto v0.0.0-20220414192740-2d67ff6cf2b4 // indirect
)
