package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"syscall"

	"google.golang.org/grpc"
   	"google.golang.org/grpc/reflection"
	log "github.com/sirupsen/logrus"
	pb "google.golang.org/grpc/examples/helloworld/helloworld"
    tracing "github.com/ease-lab/vhive/utils/tracing/go"
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

// server is used to implement helloworld.GreeterServer.
type server struct {
	pb.UnimplementedGreeterServer
}

// SayHello implements helloworld.GreeterServer
func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	// log.Printf("Received: %v", in.GetName())
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
	// log.Printf("Start server: listen on : %s\n", address)
	if port, ok := os.LookupEnv("GRPC_PORT"); ok {
		address += port
	} else {
		address += default_port
	}

    if tracing.IsTracingEnabled(){
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
