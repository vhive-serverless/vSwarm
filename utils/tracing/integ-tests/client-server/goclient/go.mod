module tests/tracing/python/client-server

go 1.16

replace (
	github.com/ease-lab/vSwarm/examples/protobuf/helloworld => ../../../../protobuf/helloworld
	github.com/ease-lab/vSwarm/utils/tracing/go => ../../../go
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc => go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.20.0
)

require (
	github.com/containerd/containerd v1.5.8
	github.com/ease-lab/vSwarm/examples/protobuf/helloworld v0.0.0-00010101000000-000000000000
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-00010101000000-000000000000
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.20.0
	google.golang.org/grpc v1.39.0
)
