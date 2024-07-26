module test-client

go 1.21.4

replace github.com/vhive-serverless/vSwarm/utils/protobuf/helloworld => ../../utils/protobuf/helloworld

require (
	github.com/vhive-serverless/vSwarm/utils/protobuf/helloworld v0.0.0-00010101000000-000000000000
	google.golang.org/grpc v1.65.0
)

require (
	golang.org/x/net v0.27.0 // indirect
	golang.org/x/sys v0.22.0 // indirect
	golang.org/x/text v0.16.0 // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20240725223205-93522f1f2a9f // indirect
	google.golang.org/protobuf v1.34.2 // indirect
)
