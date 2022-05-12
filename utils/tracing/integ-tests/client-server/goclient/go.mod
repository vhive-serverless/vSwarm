module tests/tracing/python/client-server

go 1.16

require (
	github.com/containerd/containerd v1.6.2
	github.com/ease-lab/vSwarm-proto v0.1.3
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-20220427112636-f8f3fc171804
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.31.0
	google.golang.org/grpc v1.46.0
)
