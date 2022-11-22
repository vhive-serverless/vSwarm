module auth

go 1.16

replace github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go

require (
	github.com/sirupsen/logrus v1.9.0
	github.com/vhive-serverless/vSwarm-proto v0.3.0
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-00010101000000-000000000000
	google.golang.org/grpc v1.49.0
)
