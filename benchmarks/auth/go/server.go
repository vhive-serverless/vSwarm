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

package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"syscall"

	pb "github.com/ease-lab/vSwarm/benchmarks/auth/proto"

	tracing "github.com/ease-lab/vSwarm/utils/tracing/go"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

const (
	default_port = "50051"
)

type Statement struct {
	Action   string
	Effect   string
	Resource string
}
type policyDocument struct {
	Version   string
	Statement []Statement
}
type Context struct {
	stringKey  string
	numberKey  int
	booleanKey bool
}
type authResponse struct {
	principalId    string
	policyDocument policyDocument
	context        Context
}

func generatePolicy(principalId, effect, resource string) authResponse {
	var authResponse authResponse

	authResponse.principalId = principalId
	if effect != "" && resource != "" {
		var policyDocument policyDocument
		policyDocument.Version = "2012-10-17"
		// policyDocument.Statement = []
		var statementOne Statement
		statementOne.Action = "execute-api:Invoke"
		statementOne.Effect = effect
		statementOne.Resource = resource
		policyDocument.Statement = []Statement{statementOne}
		authResponse.policyDocument = policyDocument
	}

	// Optional output with custom properties of the String, Number or Boolean type.
	authResponse.context = Context{stringKey: "stringval", numberKey: 123, booleanKey: true}
	return authResponse
}

// server is used to implement auth.GreeterServer.
type server struct {
	pb.UnimplementedGreeterServer
}

// SayHello implements auth.GreeterServer
func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	gid := syscall.Getgid()
	token := in.GetName()
	fakeMethodArn := "arn:aws:execute-api:{regionId}:{accountId}:{apiId}/{stage}/{httpVerb}/[{resource}/[{child-resources}]]"
	var msg string
	var ret authResponse

	switch token {
	case ".f2":
		ret = generatePolicy("user", "Allow", fakeMethodArn)
		msg = "auth.f2"
	default: // case ".f1":
		ret = generatePolicy("user", "Deny", fakeMethodArn)
		msg = "auth.f1"
	}

	resp := fmt.Sprintf("Serve Function: Golang.%s, from GID: %d.  Additional message: %s", msg, gid, ret.context.stringKey)
	return &pb.HelloReply{Message: resp}, nil
}

func main() {

	var address string = ":"
	if port, ok := os.LookupEnv("GRPC_PORT"); ok {
		address += port
	} else {
		address += default_port
	}

	if tracing.IsTracingEnabled() {
		shutdown, err := tracing.InitBasicTracer("http://localhost:9411/api/v2/spans", "auth function")
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
