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
	"fmt"
	"net"
	"os"

	pb "github.com/ease-lab/vSwarm-proto/proto/helloworld"

	log "github.com/sirupsen/logrus"

	grpcClients "github.com/ease-lab/vSwarm-proto/grpcclient"
	tracing "github.com/ease-lab/vSwarm/utils/tracing/go"

	"google.golang.org/grpc"
)

type server struct {
	pb.UnimplementedGreeterServer
}

// Create a variable for the client here
var grpcClient grpcClients.GrpcClient

var address = flag.String("addr", "0.0.0.0:50000", "Specify the HOST:PORT for relay server to listen at")

// var proto = flag.String("proto", "proto/helloworld.proto", "Specify the protocol file to use")
var functionName = flag.String("function-name", "helloworld", "Specify the name of the function being invoked.")
var functionEndpointURL = flag.String("function-endpoint-url", "0.0.0.0", "Specify the function endpoint URL (HOST) to call at")
var functionEndpointPort = flag.String("function-endpoint-port", "50051", "Specify the function endpoint port to call at")
var zipkin = flag.String("zipkin", "http://localhost:9411/api/v2/spans", "zipkin url")

func isDebuggingEnabled() bool {
	if val, ok := os.LookupEnv("ENABLE_DEBUGGING"); !ok || val == "false" {
		return false
	} else if val == "true" {
		return true
	} else {
		log.Fatalf("ENABLE_DEBUGGING has unexpected value: `%s`", val)
		return false
	}
}

func main() {
	flag.Parse()

	if isDebuggingEnabled() {
		log.SetLevel(log.DebugLevel)
		log.Info("Debugging is enabled.")
	}

	if tracing.IsTracingEnabled() {
		log.Printf("Start tracing on : %s\n", *zipkin)
		tracerName := fmt.Sprint("Relay server for ", *functionName)
		shutdown, err := tracing.InitBasicTracer(*zipkin, tracerName)
		if err != nil {
			log.Warn(err)
		}
		defer shutdown()
	}

	// Establish and initialize connection to the downstream function
	serviceName := grpcClients.FindServiceName(*functionName)
	grpcClient = grpcClients.FindGrpcClient(serviceName)
	grpcClient.Init(*functionEndpointURL, *functionEndpointPort)
	defer grpcClient.Close()

	// Register the Greeter Service with the server
	var grpcServer *grpc.Server
	if tracing.IsTracingEnabled() {
		grpcServer = tracing.GetGRPCServerWithUnaryInterceptor()
	} else {
		grpcServer = grpc.NewServer()
	}
	pb.RegisterGreeterServer(grpcServer, &server{})

	// Start listening for invocations
	var listener, err = net.Listen("tcp", *address)
	if err != nil {
		log.Fatalf("Failed to listen at %v", err)
	}
	defer listener.Close()

	log.Printf("Started relay server at %s", *address)

	if err := grpcServer.Serve(listener); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	log.Info("Received: ", in.GetName())
	// log.Debug("Received: ", in.GetVHiveMetadata())

	replyBack := SendMessageToBenchmark(in)

	return &pb.HelloReply{Message: replyBack}, nil
}

func SendMessageToBenchmark(in *pb.HelloRequest) string {
	reply := grpcClient.Request(in.GetName())
	log.Debug(reply)
	return reply
}
