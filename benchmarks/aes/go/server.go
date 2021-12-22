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
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"syscall"

	"google.golang.org/grpc"
	pb "google.golang.org/grpc/examples/helloworld/helloworld"
)

const (
	default_port = "50051"
)

func AES(plaintext []byte) []byte {
	// Reference: cipher documentation
	// https://golang.org/pkg/crypto/cipher/#BlockMode

	key, _ := hex.DecodeString("6368616e676520746869732070617373")

	// CBC mode works on blocks so plaintexts may need to be padded to the
	// next whole block. For an example of such padding, see
	// https://tools.ietf.org/html/rfc5246#section-6.2.3.2.
	// For simplicity, here we'll assume that the plaintext
	// is already of the correct length.
	if len(plaintext)%aes.BlockSize != 0 {
		panic("plaintext is not a multiple of the block size")
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		panic(err)
	}

	// IV: initialization vector that is generated randomly.
	// This will make the encryption result different from time to time
	ciphertext := make([]byte, aes.BlockSize+len(plaintext))
	iv := ciphertext[:aes.BlockSize]
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		panic(err)
	}

	mode := cipher.NewCBCEncrypter(block, iv)
	mode.CryptBlocks(ciphertext[aes.BlockSize:], plaintext)

	return ciphertext
}

func f1() (string, []byte, []byte) {
	plaintext := []byte("exampleplaintext")
	ciphertext := AES(plaintext)
	return "GoLang.aes.f1", plaintext, ciphertext
}
func f2() (string, []byte, []byte) {
	plaintext := []byte("a m e s s a g e ")
	ciphertext := AES(plaintext)
	return "GoLang.aes.f2", plaintext, ciphertext
}
func fn(plaintext []byte) (string, []byte, []byte) {
	ciphertext := AES(plaintext)
	return "GoLang.aes.fn(plaintext)", plaintext, ciphertext
}

// server is used to implement helloworld.GreeterServer.
type server struct {
	pb.UnimplementedGreeterServer
}

// SayHello implements helloworld.GreeterServer
func (s *server) SayHello(ctx context.Context, in *pb.HelloRequest) (*pb.HelloReply, error) {
	// log.Printf("Received: %v", in.GetName())
	gid := syscall.Getgid()
	var msg string
	var plaintext, ciphertext []byte
	switch in.GetName() {
	case ".f2":
		msg, plaintext, ciphertext = f2()
	case "", ".f1":
		msg, plaintext, ciphertext = f1()
	default:
		plaintext = []byte(in.GetName())
		var padding [aes.BlockSize]byte
		plaintext = append(plaintext, padding[(len(plaintext)%aes.BlockSize):]...)
		msg, plaintext, ciphertext = fn(plaintext)
	}
	resp := fmt.Sprintf("Hello: this is: %d. Invoke %s | Plaintext: %s Ciphertext: %x", gid, msg, plaintext, ciphertext)
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

	lis, err := net.Listen("tcp", address)
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	log.Printf("Start server: listen on : %s\n", address)

	s := grpc.NewServer()
	pb.RegisterGreeterServer(s, &server{})

	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
