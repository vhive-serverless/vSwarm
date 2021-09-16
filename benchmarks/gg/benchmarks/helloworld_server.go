package main

import (
	"bytes"
	"context"
	"flag"
	"fmt"
	"log"
	"net"
	"os"
	"os/exec"

	"google.golang.org/grpc"
	pb "google.golang.org/grpc/examples/helloworld/helloworld"
	"google.golang.org/grpc/reflection"
)

var addr *string
var port *string

type server struct {
	pb.UnimplementedGreeterServer
}

func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	log.Printf("Received request : %v", in.GetName())

	log.Printf("running gg script.")
	var target string
	if targetVar, ok := os.LookupEnv("target"); !ok {
		target = "fibonacci"
	} else {
		target = targetVar
	}
	script := fmt.Sprintf("/app/%s/bin/run-vhive.sh", target)

	cmd := exec.Command("/bin/bash", script, *addr, *port, "1")
	var out bytes.Buffer
	var stderr bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &stderr
	err := cmd.Run()
	if err != nil {
		log.Fatalf(fmt.Sprint(err) + ": " + stderr.String())
	}
	log.Printf("stdout Result: " + out.String())
	log.Printf("stderr Result: " + stderr.String())

	return &pb.HelloReply{Message: "Hello " + in.GetName()}, nil
}

func main() {
	addr = flag.String("addr", "gg-port-0.default.svc.cluster.local", "Decoder address")
	servePort := flag.String("ps", ":80", "Decoder port")
	port = flag.String("p", "80", "Decoder port")

	flag.Parse()

	lis, err := net.Listen("tcp", *servePort)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	s := grpc.NewServer()
	pb.RegisterGreeterServer(s, &server{})
	reflection.Register(s)
	log.Printf("server listening at %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
