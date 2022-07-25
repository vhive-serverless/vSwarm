module auth

go 1.16

replace github.com/ease-lab/vSwarm/utils/tracing/go => ../../utils/tracing/go

require (
	github.com/ease-lab/vSwarm-proto v0.2.0
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-20220719164711-8782cc0ff194
	github.com/sirupsen/logrus v1.9.0
	google.golang.org/grpc v1.48.0
)
