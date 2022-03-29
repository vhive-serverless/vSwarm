module github.com/ease-lab/vhive/examples/deployer

go 1.16

replace github.com/ease-lab/vhive/examples/endpoint => ../endpoint

require (
	github.com/ease-lab/vhive/examples/endpoint v0.0.0-20220315183234-1c8a70fc7019
	github.com/sirupsen/logrus v1.8.1
)
