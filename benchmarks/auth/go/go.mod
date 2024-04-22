module auth

go 1.21

replace github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../../utils/tracing/go

require (
	github.com/aws/aws-lambda-go v1.47.0
	github.com/sirupsen/logrus v1.9.3
	github.com/vhive-serverless/vSwarm-proto v0.5.0
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-20240422181019-5b1711d87c5d
	google.golang.org/grpc v1.63.2
)

require (
	github.com/go-logr/logr v1.4.1 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/openzipkin/zipkin-go v0.4.2 // indirect
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.50.0 // indirect
	go.opentelemetry.io/otel v1.25.0 // indirect
	go.opentelemetry.io/otel/exporters/zipkin v1.25.0 // indirect
	go.opentelemetry.io/otel/metric v1.25.0 // indirect
	go.opentelemetry.io/otel/sdk v1.25.0 // indirect
	go.opentelemetry.io/otel/trace v1.25.0 // indirect
	golang.org/x/net v0.24.0 // indirect
	golang.org/x/sys v0.19.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20240415180920-8c6c420018be // indirect
	google.golang.org/protobuf v1.33.0 // indirect
)
