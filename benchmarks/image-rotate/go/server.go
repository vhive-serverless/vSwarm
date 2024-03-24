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
	"flag"
	"fmt"
	"os"
	"net"
	"strings"

	"github.com/disintegration/imaging"
	log "github.com/sirupsen/logrus"
	pb "github.com/vhive-serverless/vSwarm-proto/proto/image_rotate"
	tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"

	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
)

var (
	zipkin        = flag.String("zipkin", "http://localhost:9411/api/v2/spans", "zipkin url")
	address       = flag.String("addr", "0.0.0.0:50051", "Address:Port the grpc server is listening to")
	default_image = flag.String("default-image", "default.jpg", "Default image to be rotated if empty")
)

func imageRotate(imgPath string, imgOutPath string) string {
	src, err := imaging.Open(imgPath)
	if err != nil {
		log.Warnf("failed to open image: %v", err)
		errorMessage := "go.image_rotate.ImageNotFound.Error:" + err.Error()
		return errorMessage
	}
	rotatedImage := imaging.Rotate90(src)
	err = imaging.Save(rotatedImage, imgOutPath)
	if err != nil {
		log.Warnf("failed to save image: %v", err)
		errorMessage := "go.image_rotate.ImageNotSaved.Error:" + err.Error()
		return errorMessage
	}
	message := "go.image_rotate." + imgPath
	return message
}

type server struct {
	pb.UnimplementedImageRotateServer
}

func (s *server) RotateImage(ctx context.Context, in *pb.SendImage) (*pb.GetRotatedImage, error) {
	var imgPath string
	var imgOutPath string
	if in.GetName() == "" {
		imgPath = "images/" + *default_image
	} else {
		imgPath = "images/" + in.GetName()
	}
	imgOutPath = "images/out.jpg"
	message := imageRotate(imgPath, imgOutPath)
	resp := fmt.Sprintf("fn: ImageRotate | image: %s | return msg: %s | runtime: Go", imgPath, message)
	return &pb.GetRotatedImage{Message: resp}, nil
}

func main() {
	val, ok := os.LookupEnv("IS_LAMBDA")
	LAMBDA := (ok && (strings.ToLower(val) == "true" || strings.ToLower(val) == "yes" || strings.ToLower(val) == "1"))
	if LAMBDA {
	} else {
		flag.Parse()
		if tracing.IsTracingEnabled() {
			log.Printf("Start tracing on : %s\n", *zipkin)
			shutdown, err := tracing.InitBasicTracer(*zipkin, "image-rotate function")
			if err != nil {
					log.Warn(err)
			}
			defer shutdown()
		}
		lis, err := net.Listen("tcp", *address)
		if err != nil {
				log.Fatalf("failed to listen: %v", err)
		}
		log.Printf("Start ImageRotate-go server. Addr: %s\n", *address)
		var grpcServer *grpc.Server
		if tracing.IsTracingEnabled() {
				grpcServer = tracing.GetGRPCServerWithUnaryInterceptor()
		} else {
				grpcServer = grpc.NewServer()
		}
		pb.RegisterImageRotateServer(grpcServer, &server{})
		reflection.Register(grpcServer)
		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("failed to serve: %v", err)
		}
	}
}