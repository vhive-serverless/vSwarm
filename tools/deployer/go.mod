module github.com/vhive-serverless/vSwarm/tools/deployer

go 1.16

replace github.com/vhive-serverless/vSwarm/tools/endpoint => ../endpoint

require (
	github.com/sirupsen/logrus v1.9.0
	github.com/vhive-serverless/vSwarm/tools/endpoint v0.0.0-00010101000000-000000000000
)
