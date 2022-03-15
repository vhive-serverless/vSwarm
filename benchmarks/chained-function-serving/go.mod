module tests/chained-functions-serving

go 1.16

replace (
	github.com/ease-lab/vSwarm/examples/protobuf/helloworld => ../../utils/protobuf/helloworld
	github.com/ease-lab/vSwarm/utils/tracing/go => ../../utils/tracing/go
	github.com/ease-lab/vhive-xdt/proto/crossXDT => github.com/ease-lab/vhive-xdt/proto/crossXDT v0.0.0-20210903135911-a8dd405a02ec
	github.com/ease-lab/vhive-xdt/proto/downXDT => github.com/ease-lab/vhive-xdt/proto/downXDT v0.0.0-20210903135911-a8dd405a02ec
	github.com/ease-lab/vhive-xdt/proto/upXDT => github.com/ease-lab/vhive-xdt/proto/upXDT v0.0.0-20210903135911-a8dd405a02ec
	github.com/ease-lab/vhive-xdt/utils => github.com/ease-lab/vhive-xdt/utils v0.0.0-20210903135911-a8dd405a02ec
	tests/chained-functions-serving/proto => ./proto
)

require (
	cloud.google.com/go v0.81.0 // indirect
	github.com/aws/aws-sdk-go v1.40.16
	github.com/containerd/containerd v1.5.8
	github.com/ease-lab/vhive-xdt/sdk/golang v0.0.0-20210903135911-a8dd405a02ec
	github.com/ease-lab/vhive-xdt/utils v0.0.0-00010101000000-000000000000
	github.com/ease-lab/vhive/utils/tracing/go v0.0.0-20210727103631-f5f1ba9920c2 // indirect
	github.com/openzipkin/zipkin-go v0.4.0 // indirect
	github.com/sirupsen/logrus v1.8.1
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.31.0
	go.opentelemetry.io/otel/sdk v1.6.3 // indirect
	golang.org/x/net v0.0.0-20220412020605-290c469a71a5 // indirect
	golang.org/x/oauth2 v0.0.0-20210402161424-2e8d93401602 // indirect
	golang.org/x/sys v0.0.0-20220412211240-33da011f77ad // indirect
	google.golang.org/genproto v0.0.0-20220414192740-2d67ff6cf2b4 // indirect
	google.golang.org/grpc v1.45.0
	google.golang.org/protobuf v1.28.0
)
