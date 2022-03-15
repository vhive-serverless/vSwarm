module github.com/ease-lab/vSwarm/tools/deployer

go 1.16

replace github.com/ease-lab/vSwarm/tools/endpoint => ../endpoint

require (
	github.com/ease-lab/vSwarm/tools/endpoint v0.0.0-00010101000000-000000000000
	github.com/sirupsen/logrus v1.8.1
	github.com/stretchr/testify v1.7.1 // indirect
	golang.org/x/sys v0.0.0-20220412211240-33da011f77ad // indirect
	gopkg.in/yaml.v3 v3.0.0-20210107192922-496545a6307b // indirect
)
