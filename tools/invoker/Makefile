invoker: client.go measure.go helloworld.pb.go helloworld_grpc.pb.go
	go mod tidy
	go build github.com/vhive-serverless/vSwarm/tools/invoker

helloworld.pb.go: proto/helloworld.proto
	protoc \
		--go_out=. \
		--go_opt="paths=source_relative" \
		proto/helloworld.proto

helloworld_grpc.pb.go: proto/helloworld.proto
	protoc \
		--go-grpc_out=. \
		--go-grpc_opt="paths=source_relative" \
		proto/helloworld.proto