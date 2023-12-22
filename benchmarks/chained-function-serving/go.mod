module tests/chained-functions-serving

go 1.21

replace (
	github.com/ease-lab/vhive-xdt/proto/crossXDT => github.com/ease-lab/vhive-xdt/proto/crossXDT v0.0.0-20221107151004-a0940018d178
	github.com/ease-lab/vhive-xdt/proto/downXDT => github.com/ease-lab/vhive-xdt/proto/downXDT v0.0.0-20221107151004-a0940018d178
	github.com/ease-lab/vhive-xdt/proto/upXDT => github.com/ease-lab/vhive-xdt/proto/upXDT v0.0.0-20221107151004-a0940018d178
	github.com/ease-lab/vhive-xdt/utils => github.com/ease-lab/vhive-xdt/utils v0.0.0-20221107151004-a0940018d178
	github.com/vhive-serverless/vSwarm/examples/protobuf/helloworld => ../../utils/protobuf/helloworld
	github.com/vhive-serverless/vSwarm/utils/storage/go => ../../utils/storage/go
	github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go
	go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp => go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.32.0
	tests/chained-functions-serving/proto => ./proto
)

require (
	github.com/containerd/containerd v1.6.12
	github.com/ease-lab/vhive-xdt/sdk/golang v0.0.0-20221107151004-a0940018d178
	github.com/ease-lab/vhive-xdt/utils v0.0.0-20221107151004-a0940018d178
	github.com/sirupsen/logrus v1.9.3
	github.com/vhive-serverless/vSwarm/examples/protobuf/helloworld v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/utils/storage/go v0.0.0-00010101000000-000000000000
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-00010101000000-000000000000
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.46.1
	google.golang.org/grpc v1.60.1
	google.golang.org/protobuf v1.31.0
)

require (
	cloud.google.com/go/compute v1.23.1 // indirect
	github.com/aws/aws-sdk-go v1.46.7 // indirect
	github.com/cespare/xxhash/v2 v2.2.0 // indirect
	github.com/dgryski/go-rendezvous v0.0.0-20200823014737-9f7001d12a5f // indirect
	github.com/ease-lab/vSwarm/utils/tracing/go v0.0.0-20220609140039-b4da20ea6b36 // indirect
	github.com/ease-lab/vhive-xdt/proto/crossXDT v0.0.0-00010101000000-000000000000 // indirect
	github.com/ease-lab/vhive-xdt/proto/downXDT v0.0.0-00010101000000-000000000000 // indirect
	github.com/ease-lab/vhive-xdt/proto/upXDT v0.0.0-00010101000000-000000000000 // indirect
	github.com/go-logr/logr v1.3.0 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/go-redis/redis/v8 v8.11.5 // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/jmespath/go-jmespath v0.4.0 // indirect
	github.com/kelseyhightower/envconfig v1.4.0 // indirect
	github.com/openzipkin/zipkin-go v0.4.2 // indirect
	github.com/pkg/errors v0.9.1 // indirect
	go.opentelemetry.io/otel v1.21.0 // indirect
	go.opentelemetry.io/otel/exporters/zipkin v1.21.0 // indirect
	go.opentelemetry.io/otel/metric v1.21.0 // indirect
	go.opentelemetry.io/otel/sdk v1.21.0 // indirect
	go.opentelemetry.io/otel/trace v1.21.0 // indirect
	go.uber.org/atomic v1.9.0 // indirect
	golang.org/x/net v0.18.0 // indirect
	golang.org/x/sys v0.14.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20231030173426-d783a09b4405 // indirect
)
