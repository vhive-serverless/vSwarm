module test-client

go 1.21.4

replace github.com/vhive-serverless/vSwarm/utils/protobuf/helloworld => ../../utils/protobuf/helloworld

require (
	github.com/vhive-serverless/vSwarm/utils/protobuf/helloworld v0.0.0-00010101000000-000000000000
	google.golang.org/grpc v1.67.1
)

require (
	golang.org/x/net v0.30.0 // indirect
	golang.org/x/sys v0.26.0 // indirect
	golang.org/x/text v0.19.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20240930140551-af27646dc61f // indirect
	google.golang.org/protobuf v1.34.2 // indirect
)
