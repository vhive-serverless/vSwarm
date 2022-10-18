module github.com/vhive-serverless/vSwarm/tools/relay

go 1.16

replace github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go

require (
	github.com/sirupsen/logrus v1.9.0
	github.com/vhive-serverless/vSwarm-proto v0.3.0
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-20220719164711-8782cc0ff194
	google.golang.org/grpc v1.48.0
)
