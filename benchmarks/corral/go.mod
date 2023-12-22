module tests/word_count/v2

go 1.21

replace (
	github.com/bcongdon/corral => github.com/ease-lab/corral v0.0.0-20221114011422-c2c72270c3e8
	github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go
)

require (
	github.com/bcongdon/corral v0.0.0-20210528162701-3b296bdfd98d
	github.com/sirupsen/logrus v1.9.3
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-20221114010759-4b33d106fe5b
	google.golang.org/grpc v1.60.1
	google.golang.org/protobuf v1.31.0
)

require (
	cloud.google.com/go/compute/metadata v0.2.3 // indirect
	github.com/aws/aws-lambda-go v1.25.0 // indirect
	github.com/aws/aws-sdk-go v1.40.7 // indirect
	github.com/dustin/go-humanize v1.0.0 // indirect
	github.com/fsnotify/fsnotify v1.4.9 // indirect
	github.com/go-logr/logr v1.3.0 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/hashicorp/golang-lru v0.5.4 // indirect
	github.com/hashicorp/hcl v1.0.0 // indirect
	github.com/jmespath/go-jmespath v0.4.0 // indirect
	github.com/magiconair/properties v1.8.5 // indirect
	github.com/mattetti/filebuffer v1.0.1 // indirect
	github.com/mattn/go-runewidth v0.0.12 // indirect
	github.com/mitchellh/mapstructure v1.4.1 // indirect
	github.com/openzipkin/zipkin-go v0.4.2 // indirect
	github.com/pelletier/go-toml v1.9.3 // indirect
	github.com/rivo/uniseg v0.1.0 // indirect
	github.com/spf13/afero v1.6.0 // indirect
	github.com/spf13/cast v1.3.1 // indirect
	github.com/spf13/jwalterweatherman v1.1.0 // indirect
	github.com/spf13/pflag v1.0.5 // indirect
	github.com/spf13/viper v1.8.1 // indirect
	github.com/subosito/gotenv v1.2.0 // indirect
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.46.1 // indirect
	go.opentelemetry.io/otel v1.21.0 // indirect
	go.opentelemetry.io/otel/exporters/zipkin v1.21.0 // indirect
	go.opentelemetry.io/otel/metric v1.21.0 // indirect
	go.opentelemetry.io/otel/sdk v1.21.0 // indirect
	go.opentelemetry.io/otel/trace v1.21.0 // indirect
	golang.org/x/net v0.18.0 // indirect
	golang.org/x/sync v0.4.0 // indirect
	golang.org/x/sys v0.14.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20231002182017-d307bd883b97 // indirect
	gopkg.in/cheggaaa/pb.v1 v1.0.28 // indirect
	gopkg.in/ini.v1 v1.62.0 // indirect
	gopkg.in/yaml.v2 v2.4.0 // indirect
)
