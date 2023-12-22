module auth

go 1.21

replace github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../../utils/tracing/go

require (
	github.com/aws/aws-lambda-go v1.41.0
	github.com/sirupsen/logrus v1.9.3
	github.com/vhive-serverless/vSwarm-proto v0.4.2
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-20231030155054-d3b2e7d0ff16
	google.golang.org/grpc v1.60.1
)

require (
	github.com/go-logr/logr v1.3.0 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/golang/protobuf v1.5.3 // indirect
	github.com/openzipkin/zipkin-go v0.4.2 // indirect
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.46.1 // indirect
	go.opentelemetry.io/otel v1.21.0 // indirect
	go.opentelemetry.io/otel/exporters/zipkin v1.21.0 // indirect
	go.opentelemetry.io/otel/metric v1.21.0 // indirect
	go.opentelemetry.io/otel/sdk v1.21.0 // indirect
	go.opentelemetry.io/otel/trace v1.21.0 // indirect
	golang.org/x/net v0.18.0 // indirect
	golang.org/x/sys v0.14.0 // indirect
	golang.org/x/text v0.14.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20231030173426-d783a09b4405 // indirect
	google.golang.org/protobuf v1.31.0 // indirect
)
