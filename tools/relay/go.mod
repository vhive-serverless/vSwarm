module github.com/ease-lab/vSwarm/tools/relay

go 1.16

replace github.com/ease-lab/vSwarm/utils/tracing/go => ../../utils/tracing/go

require (
	github.com/ease-lab/vSwarm-proto v0.2.0
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-20220510183615-46769f6d03ae
	github.com/sirupsen/logrus v1.8.1
	google.golang.org/grpc v1.47.0
)
