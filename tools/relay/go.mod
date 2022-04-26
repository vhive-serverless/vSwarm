module github.com/ease-lab/vSwarm/tools/relay

go 1.16

replace github.com/ease-lab/vSwarm/utils/tracing/go => ../../utils/tracing/go

require (
	github.com/ease-lab/vSwarm-proto v0.0.0-20220425132824-72aa8060e781
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-20220421212014-f17df208fc40
	github.com/sirupsen/logrus v1.8.1
	google.golang.org/grpc v1.46.0
)
