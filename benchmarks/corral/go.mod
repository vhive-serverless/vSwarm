module tests/word_count

go 1.16

replace (
	github.com/bcongdon/corral => github.com/ease-lab/corral v0.0.0-20210730111132-e1dcd31f1680
	github.com/ease-lab/vSwarm/utils/tracing/go => ../../utils/tracing/go
)

require (
	github.com/bcongdon/corral v0.0.0-00010101000000-000000000000
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-00010101000000-000000000000
	github.com/sirupsen/logrus v1.8.1
	google.golang.org/grpc v1.45.0
	google.golang.org/protobuf v1.27.1
)
