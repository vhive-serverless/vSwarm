module github.com/ease-lab/vSwarm/tools/deployer

go 1.16

replace github.com/ease-lab/vSwarm/tools/endpoint => ../endpoint

require (
	github.com/ease-lab/vSwarm/tools/endpoint v0.0.0-20220719164711-8782cc0ff194
	github.com/sirupsen/logrus v1.9.0
	github.com/stretchr/testify v1.7.1 // indirect
	golang.org/x/sys v0.0.0-20220722155257-8c9f86f7a55f // indirect
	gopkg.in/yaml.v3 v3.0.0-20210107192922-496545a6307b // indirect
)
