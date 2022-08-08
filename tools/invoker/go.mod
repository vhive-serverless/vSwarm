module github.com/ease-lab/vSwarm/tools/invoker

go 1.16

replace (
	github.com/ease-lab/vSwarm/tools/benchmarking_eventing => ../benchmarking_eventing
	github.com/ease-lab/vSwarm/tools/endpoint => ../endpoint
	github.com/ease-lab/vSwarm/tools/invoker/proto => ./proto
	github.com/ease-lab/vSwarm/utils/tracing/go => ../../utils/tracing/go
)

require (
	github.com/containerd/containerd v1.6.6
	github.com/ease-lab/vSwarm/tools/benchmarking_eventing v0.0.0-20220719164711-8782cc0ff194
	github.com/ease-lab/vSwarm/tools/endpoint v0.0.0-20220719164711-8782cc0ff194
	github.com/ease-lab/vSwarm/tools/invoker/proto v0.0.0-20220719164711-8782cc0ff194
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-20220719164711-8782cc0ff194
	github.com/golang/protobuf v1.5.2
	github.com/google/uuid v1.3.0
	github.com/sirupsen/logrus v1.9.0
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.34.0
	google.golang.org/grpc v1.48.0
)
