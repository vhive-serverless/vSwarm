// MIT License

// Copyright (c) 2022 EASE lab

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// Package main implements a server for Greeter service.
package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"strconv"
	"syscall"

	tracing "github.com/ease-lab/vhive/utils/tracing/go"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	pb "google.golang.org/grpc/examples/helloworld/helloworld"
	"google.golang.org/grpc/reflection"
)

const (
	default_port = "50051"
)

func fibonacci(num int) float64 {
	var num1 float64 = 0
	var num2 float64 = 1
	var sum float64
	for i := 0; i < num; i++ {
		sum = num1 + num2
		num1 = num2
		num2 = sum
	}
	return num1
}

// server is used to implement helloworld.GreeterServer.
type server struct {
	pb.UnimplementedGreeterServer
}

// SayHello implements helloworld.GreeterServer
func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	// log.Printf("Received: %v", in.GetName())
	gid := syscall.Getgid()
	x, _ := strconv.ParseInt(in.GetName(), 10, 64)
	var y = fibonacci(int(x))
	resp := fmt.Sprintf("Hello: this is: %d. Invoke GoLang Fib y = fib(x) | x: %d y: %.1f", gid, x, y)
	return &pb.HelloReply{Message: resp}, nil
}

func main() {

	var address string = ":"
	// log.Printf("Start server: listen on : %s\n", address)
	if port, ok := os.LookupEnv("GRPC_PORT"); ok {
		address += port
	} else {
		address += default_port
	}

	if tracing.IsTracingEnabled() {
		shutdown, err := tracing.InitBasicTracer("http://localhost:9411/api/v2/spans", "fibonacci function")
		if err != nil {
			log.Warn(err)
		}
		defer shutdown()
	}

	lis, err := net.Listen("tcp", address)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	log.Printf("Start server: listen on : %s\n", address)

	var grpcServer *grpc.Server
	if tracing.IsTracingEnabled() {
		grpcServer = tracing.GetGRPCServerWithUnaryInterceptor()
	} else {
		grpcServer = grpc.NewServer()
	}
	pb.RegisterGreeterServer(grpcServer, &server{})
	reflection.Register(grpcServer)

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
