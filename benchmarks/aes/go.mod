module aes

go 1.16

replace (
	aes/proto => ./proto
	github.com/ease-lab/vSwarm/utils/tracing/go => ../../utils/tracing/go
)

require (
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-00010101000000-000000000000
	github.com/sirupsen/logrus v1.8.1
	google.golang.org/grpc v1.44.0
	google.golang.org/protobuf v1.27.1
)
