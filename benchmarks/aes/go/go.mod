module server

go 1.16

// replace github.com/ease-lab/vSwarm/utils/tracing/go => ../../../utils/tracing/go

require (
	github.com/ease-lab/vhive/utils/tracing/go v0.0.0-20220214164914-781b0b88b21b
	github.com/sirupsen/logrus v1.8.1
	google.golang.org/grpc v1.44.0
	google.golang.org/grpc/examples v0.0.0-20220224182858-328efcc9276e
)
