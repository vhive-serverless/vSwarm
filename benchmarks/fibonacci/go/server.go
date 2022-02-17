/*
 *
 * Copyright 2015 gRPC authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

// Package main implements a server for Greeter service.
package main

import (
	"context"
	"log"
	"os"
	"net"
	"syscall"
	"fmt"
	"strconv"

	"google.golang.org/grpc"
   	"google.golang.org/grpc/reflection"
	log "github.com/sirupsen/logrus"
	pb "google.golang.org/grpc/examples/helloworld/helloworld"
    tracing "github.com/ease-lab/vhive/utils/tracing/go"
)

const (
	default_port = "50051"
)

func fibonacci(num int) float64{
	var num1 float64 =0;
	var num2 float64 =1;
	var sum float64;
	for i := 0; i < num; i++ {
			sum=num1+num2;
			num1=num2;
			num2=sum;
	}
	return num1;
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
	resp := fmt.Sprintf("Hello: this is: %d. Invoke GoLang Fib y = fib(x) | x: %d y: %.1f", gid, x,y)
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

    if tracing.IsTracingEnabled(){
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
    if tracing.IsTracingEnabled(){
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
