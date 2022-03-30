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
	"crypto/aes"
	"crypto/cipher"
	"encoding/hex"
	"flag"
	"fmt"

	"net"

	log "github.com/sirupsen/logrus"

	pb "aes/proto"

	tracing "github.com/ease-lab/vSwarm/utils/tracing/go"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

var (
	zipkin       = flag.String("zipkin", "http://localhost:9411/api/v2/spans", "zipkin url")
	address      = flag.String("addr", "0.0.0.0:50051", "Address:Port the grpc server is listening to")
	key_string   = flag.String("key", "6368616e676520746869732070617373", "The key which is used for encryption")
	default_name = flag.String("default-plaintext", "exampleplaintext", "Default plaintext when the function is called with the name world")
)

// func AESModeCBC(plaintext []byte) []byte {
// 	// Reference: cipher documentation
// 	// https://golang.org/pkg/crypto/cipher/#BlockMode

// 	key, _ := hex.DecodeString(*key_string)

// 	// CBC mode works on blocks so plaintexts may need to be padded to the
// 	// next whole block. For an example of such padding, see
// 	// https://tools.ietf.org/html/rfc5246#section-6.2.3.2.
// 	var padding [aes.BlockSize]byte
// 	if len(plaintext)%aes.BlockSize != 0 {
// 		plaintext = append(plaintext, padding[(len(plaintext)%aes.BlockSize):]...)
// 	}

// 	block, err := aes.NewCipher(key)
// 	if err != nil {
// 		panic(err)
// 	}

// 	// The IV needs to be unique, but not secure. Therefore it's common to
// 	// include it at the beginning of the ciphertext.
// 	ciphertext := make([]byte, aes.BlockSize+len(plaintext))
// 	iv := ciphertext[:aes.BlockSize]
// 	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
// 		panic(err)
// 	}

// 	mode := cipher.NewCBCEncrypter(block, iv)
// 	mode.CryptBlocks(ciphertext[aes.BlockSize:], plaintext)

// 	return ciphertext
// }

func AESModeCTR(plaintext []byte) []byte {
	// Reference: cipher documentation
	// https://golang.org/pkg/crypto/cipher/#Stream

	key, _ := hex.DecodeString(*key_string)
	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}

	// The IV needs to be unique, but not secure. Therefore it's common to
	// include it at the beginning of the ciphertext.
	// We will use 0 to be predictable
	iv := make([]byte, aes.BlockSize)
	ciphertext := make([]byte, len(plaintext))

	stream := cipher.NewCTR(block, iv)
	stream.XORKeyStream(ciphertext, plaintext)
	return ciphertext
}

// server is used to implement helloworld.GreeterServer.
type server struct {
	pb.UnimplementedGreeterServer
}

// SayHello implements helloworld.GreeterServer
func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	// log.Printf("Received: %v", in.GetName())

	var plaintext, ciphertext []byte
	if in.GetName() == "" || in.GetName() == "world" {
		plaintext = []byte(*default_name)
	} else {
		plaintext = []byte(in.GetName())
	}
	// Do the encryption
	ciphertext = AESModeCTR(plaintext)
	resp := fmt.Sprintf("fn: AES | plaintext: %s | ciphertext: %x | runtime: golang", plaintext, ciphertext)
	return &pb.HelloReply{Message: resp}, nil
}

func main() {
	flag.Parse()

	if tracing.IsTracingEnabled() {
		log.Printf("Start tracing on : %s\n", *zipkin)
		shutdown, err := tracing.InitBasicTracer(*zipkin, "aes function")
		if err != nil {
			log.Warn(err)
		}
		defer shutdown()
	}

	lis, err := net.Listen("tcp", *address)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	log.Printf("Start AES-go server. Addr: %s\n", *address)

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
