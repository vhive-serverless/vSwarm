// MIT License
//
// Copyright (c) 2022 EASE lab
//
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

package main

import (
	"context"
	"flag"
	"net"
	"os"
	pb "helloworld/proto"

	log "github.com/sirupsen/logrus"

	"google.golang.org/grpc"
	. "relay/clients"
)

type server struct {
	pb.UnimplementedGreeterServer
}

var address = flag.String("addr", "0.0.0.0:50000", "Specify the HOST:PORT for relay server to listen at")

// var proto = flag.String("proto", "proto/helloworld.proto", "Specify the protocol file to use")
var functionName = flag.String("function-name", "helloworld", "Specify the name of the function being invoked.")
var functionEndpointURL = flag.String("function-endpoint-url", "0.0.0.0", "Specify the function endpoint URL (HOST) to call at")
var functionEndpointPort = flag.String("function-endpoint-port", "50051", "Specify the function endpoint port to call at")

func main() {
	flag.Parse()

	if os.Getenv("ENABLE_DEBUGGING") == "TRUE" {
		log.SetLevel(log.DebugLevel)
	}

	// Register the Greeter Service with the server
	var grpcServer = grpc.NewServer()
	pb.RegisterGreeterServer(grpcServer, &server{})

	// Start listening for invocations
	var listener, err = net.Listen("tcp", *address)
	defer listener.Close()
	if err != nil {
		log.Fatalf("Failed to listen at %v", err)
	}

	log.Printf("Started relay server at %s", *address)

	if err := grpcServer.Serve(listener); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	log.Info("Received: ", in.GetName())
	log.Debug("Received: ", in.GetVHiveMetadata())

	serviceName := FindServiceName(*functionName)
	grpcClient := FindGrpcClient(serviceName)
	replyBack := SendMessageToBenchmark(*functionEndpointURL, *functionEndpointPort, grpcClient, in)

	return &pb.HelloReply{Message: replyBack}, nil
}

func SendMessageToBenchmark(functionURL string, functionPort string, grpcClient GrpcClient, in *pb.HelloRequest) string {
	grpcClient.Init(functionURL, functionPort)
	
	reply := grpcClient.Request(in.GetName())
	log.Printf("%s", reply)
	
	defer grpcClient.Close()
	return reply
}
