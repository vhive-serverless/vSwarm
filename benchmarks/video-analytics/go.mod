module tests/video_analytics

go 1.16

replace (
	github.com/vhive-serverless/vSwarm/examples/protobuf/helloworld => ../../utils/protobuf/helloworld
	github.com/vhive-serverless/vSwarm/utils/storage/go => ../../utils/storage/go
	github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go
	github.com/ease-lab/vhive-xdt/proto/crossXDT => github.com/ease-lab/vhive-xdt/proto/crossXDT v0.0.0-20220612214926-3dece67094db
	github.com/ease-lab/vhive-xdt/proto/downXDT => github.com/ease-lab/vhive-xdt/proto/downXDT v0.0.0-20220612214926-3dece67094db
	github.com/ease-lab/vhive-xdt/proto/upXDT => github.com/ease-lab/vhive-xdt/proto/upXDT v0.0.0-20220612214926-3dece67094db
	github.com/ease-lab/vhive-xdt/utils => github.com/ease-lab/vhive-xdt/utils v0.0.0-20220612214926-3dece67094db
	go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp => go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.32.0
	tests/video_analytics/proto => ./proto
)

require (
	github.com/containerd/containerd v1.6.6
	github.com/vhive-serverless/vSwarm/examples/protobuf/helloworld v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/utils/storage/go v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-20220609140039-b4da20ea6b36
	github.com/ease-lab/vhive-xdt/sdk/golang v0.0.0-20220612214926-3dece67094db
	github.com/ease-lab/vhive-xdt/utils v0.0.0-00010101000000-000000000000
	github.com/sirupsen/logrus v1.9.0
	google.golang.org/grpc v1.48.0
	google.golang.org/protobuf v1.28.0
)
