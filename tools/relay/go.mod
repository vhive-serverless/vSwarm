module github.com/vhive-serverless/vSwarm/tools/relay

go 1.23.0

toolchain go1.24.12

replace github.com/vhive-serverless/vSwarm/utils/tracing/go => ../../utils/tracing/go

require (
	github.com/sirupsen/logrus v1.9.3
	github.com/vhive-serverless/vSwarm-proto v0.5.8-0.20250827062232-eba6cb9fcb46
	github.com/vhive-serverless/vSwarm/utils/tracing/go v0.0.0-20240715172541-1edab0214c9d
	google.golang.org/grpc v1.75.0
)

require (
	github.com/go-logr/logr v1.4.3 // indirect
	github.com/go-logr/stdr v1.2.2 // indirect
	github.com/google/uuid v1.6.0 // indirect
	github.com/openzipkin/zipkin-go v0.4.3 // indirect
	go.opentelemetry.io/auto/sdk v1.1.0 // indirect
	go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc v0.53.0 // indirect
	go.opentelemetry.io/otel v1.37.0 // indirect
	go.opentelemetry.io/otel/exporters/zipkin v1.28.0 // indirect
	go.opentelemetry.io/otel/metric v1.37.0 // indirect
	go.opentelemetry.io/otel/sdk v1.37.0 // indirect
	go.opentelemetry.io/otel/trace v1.37.0 // indirect
	golang.org/x/net v0.41.0 // indirect
	golang.org/x/sys v0.33.0 // indirect
	golang.org/x/text v0.26.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20250707201910-8d1bb00bc6a7 // indirect
	google.golang.org/protobuf v1.36.6 // indirect
)
