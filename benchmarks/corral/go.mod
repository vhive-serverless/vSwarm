module tests/word_count

go 1.16

replace (
	github.com/bcongdon/corral => github.com/ease-lab/corral v0.0.0-20210730111132-e1dcd31f1680
	github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go
)

require (
	github.com/aws/aws-sdk-go v1.40.16 // indirect
	github.com/bcongdon/corral v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-00010101000000-000000000000
	github.com/sirupsen/logrus v1.8.1
	golang.org/x/net v0.0.0-20220412020605-290c469a71a5 // indirect
	golang.org/x/sys v0.0.0-20220412211240-33da011f77ad // indirect
	google.golang.org/genproto v0.0.0-20220414192740-2d67ff6cf2b4 // indirect
	google.golang.org/grpc v1.45.0
	google.golang.org/protobuf v1.28.0
)
