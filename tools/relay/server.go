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
	"google.golang.org/grpc/reflection"
)

type server struct {
	pb.UnimplementedGreeterServer
}

var (
	// Arguments for the relay configuration
	address = flag.String("addr", "0.0.0.0:50000", "Specify the HOST:PORT for relay server to listen at")
	zipkin  = flag.String("zipkin", "http://localhost:9411/api/v2/spans", "zipkin url")

	// For downstream function
	// proto = flag.String("proto", "proto/helloworld.proto", "Specify the protocol file to use")
	functionName         = flag.String("function-name", "helloworld", "Specify the name of the function being invoked.")
	functionEndpointURL  = flag.String("function-endpoint-url", "0.0.0.0", "Specify the function endpoint URL (HOST) to call at")
	functionEndpointPort = flag.String("function-endpoint-port", "50051", "Specify the function endpoint port to call at")

	lowerBound      = flag.Int("lowerBound", 1, "Lower bound while generating input")
	upperBound      = flag.Int("upperBound", 10, "Upper bound while generating input")
	generatorString = flag.String("generator", "unique", "Generator type (unique / linear / random)")
	value           = flag.String("value", "helloWorld", "String input to pass to benchmark")
	functionMethod  = flag.String("function-method", "default", "Which method of benchmark to invoke")

	// Client
	grpcClient     grpcClients.GrpcClient
	inputGenerator grpcClients.Generator
)

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

	// Configure the Input generator
	inputGenerator = grpcClient.GetGenerator()
	switch *generatorString {
	case "unique":
		inputGenerator.SetGenerator(grpcClients.Unique)
	case "linear":
		inputGenerator.SetGenerator(grpcClients.Linear)
	case "random":
		inputGenerator.SetGenerator(grpcClients.Random)
	}
	inputGenerator.SetValue(*value)
	inputGenerator.SetLowerBound(*lowerBound)
	inputGenerator.SetUpperBound(*upperBound)
	inputGenerator.SetMethod(*functionMethod)

	// Register the Greeter Service with the server
	var grpcServer *grpc.Server
	if tracing.IsTracingEnabled() {
		grpcServer = tracing.GetGRPCServerWithUnaryInterceptor()
	} else {
		grpcServer = grpc.NewServer()
	}
	pb.RegisterGreeterServer(grpcServer, &server{})

	// Register reflection service on gRPC server.
	reflection.Register(grpcServer)

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
	log.Info("Received from invoker: ", in.GetName())

	// Create new packet
	pkt := inputGenerator.Next()
	log.Debug("Send to func: ", pkt)
	reply := grpcClient.Request(pkt)
	log.Debug("Recv from func: ", reply)

	return &pb.HelloReply{Message: reply}, nil
}
