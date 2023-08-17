// MIT License
//
// Copyright (c) 2021 Michal Baczun and EASE lab
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
	"errors"
	"flag"
	"fmt"
	storage "github.com/vhive-serverless/vSwarm/utils/storage/go"
	"io"
	"net"
	"os"
	"strconv"

	ctrdlog "github.com/containerd/containerd/log"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"

	pb "tests/chained-functions-serving/proto"
	pb_client "tests/chained-functions-serving/proto"

	tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"

	sdk "github.com/ease-lab/vhive-xdt/sdk/golang"
	"github.com/ease-lab/vhive-xdt/utils"
)

const (
	INLINE      = "INLINE"
	XDT         = "XDT"
	S3          = "S3"
	ELASTICACHE = "ELASTICACHE"
)

type consumerServer struct {
	transferType   string
	XDTconfig      utils.Config
	storageBackend storage.Storage
	pb.UnimplementedProducerConsumerServer
}

type ubenchServer struct {
	transferType   string
	XDTconfig      utils.Config
	storageBackend storage.Storage
	pb_client.UnimplementedProdConDriverServer
}

func fetchFromStorage(ctx context.Context, key string, storageBackend storage.Storage) (int, error) {
	span := tracing.Span{SpanName: "S3 get", TracerName: "S3 get - tracer"}
	span.StartSpan(ctx)
	defer span.EndSpan()
	log.Infof("[consumer] Fetching %s from S3", key)
	payload := storageBackend.Get(ctx, key)
	if payload == nil {
		log.Infof("Received nil object body")
		return 0, errors.New("nil Object Received")
	}

	return len(payload), nil
}

func (s *consumerServer) ConsumeByte(ctx context.Context, str *pb.ConsumeByteRequest) (*pb.ConsumeByteReply, error) {
	if tracing.IsTracingEnabled() {
		span1 := tracing.Span{SpanName: "custom-span-1", TracerName: "tracer"}
		span2 := tracing.Span{SpanName: "custom-span-2", TracerName: "tracer"}
		ctx = span1.StartSpan(ctx)
		ctx = span2.StartSpan(ctx)
		defer span1.EndSpan()
		defer span2.EndSpan()
	}
	if s.transferType == S3 || s.transferType == ELASTICACHE {
		payloadSize, err := fetchFromStorage(ctx, string(str.Value), s.storageBackend)
		if err != nil {
			return &pb.ConsumeByteReply{Value: false}, err
		} else {
			log.Printf("[consumer] Consumed %d bytes\n", payloadSize)
			return &pb.ConsumeByteReply{Value: true}, err
		}
	} else if s.transferType == INLINE {
		log.Printf("[consumer] Consumed %d bytes\n", len(str.Value))
	} else if s.transferType == XDT {
		payload, err := sdk.BroadcastGet(ctx, string(str.Value), s.XDTconfig)
		if err != nil {
			return &pb.ConsumeByteReply{Value: false}, err
		} else {
			log.Printf("[consumer] Consumed %d bytes from XDT\n", len(payload))
			return &pb.ConsumeByteReply{Value: true}, err
		}
	}
	return &pb.ConsumeByteReply{Value: true}, nil
}

func (s *consumerServer) ConsumeStream(stream pb.ProducerConsumer_ConsumeStreamServer) error {
	for {
		str, err := stream.Recv()
		if err == io.EOF {
			return stream.SendAndClose(&pb.ConsumeByteReply{Value: true})
		}
		if err != nil {
			return err
		}
		log.Printf("[consumer] Consumed string of length %d\n", len(str.Value))
	}
}

func main() {
	port := flag.Int("ps", 80, "Port")
	url := flag.String("zipkin", "http://zipkin.istio-system.svc.cluster.local:9411/api/v2/spans", "zipkin url")
	flag.Parse()

	log.SetFormatter(&log.TextFormatter{
		TimestampFormat: ctrdlog.RFC3339NanoFixed,
		FullTimestamp:   true,
	})
	log.SetOutput(os.Stdout)

	if tracing.IsTracingEnabled() {
		log.Println("consumer has tracing enabled")
		shutdown, err := tracing.InitBasicTracer(*url, "consumer")
		if err != nil {
			log.Warn(err)
		}
		defer shutdown()
	} else {
		log.Println("consumer has tracing DISABLED")
	}

	transferType, ok := os.LookupEnv("TRANSFER_TYPE")
	if !ok {
		log.Infof("TRANSFER_TYPE not found, using INLINE transfer")
		transferType = "INLINE"
	}

	var storageBackend storage.Storage
	if transferType == S3 || transferType == ELASTICACHE {
		bucketName, ok := os.LookupEnv("BUCKET_NAME")
		if !ok {
			bucketName = "vhive-prodcon-bench"
		}
		storageBackend = storage.New(transferType, bucketName)
	}

	var fanIn = false
	if value, ok := os.LookupEnv("FANIN"); ok {
		if intValue, err := strconv.Atoi(value); err == nil && intValue > 0 {
			fanIn = true
		}
	}

	var broadcast = false
	if value, ok := os.LookupEnv("BROADCAST"); ok {
		if intValue, err := strconv.Atoi(value); err == nil && intValue > 0 {
			broadcast = true
		}
	}

	if transferType == XDT && !fanIn && !broadcast {
		var handler = func(data []byte) ([]byte, bool) {
			log.Infof("gx: destination handler received data of size %d", len(data))
			log.Info("[gx] received ", data[0:9], data[len(data)-9:])
			return nil, true
		}
		config := utils.ReadConfig()
		sdk.StartDstServer(config, handler)
	} else {
		//set up server
		lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *port))
		if err != nil {
			log.Fatalf("[consumer] failed to listen: %v", err)
		}

		var grpcServer *grpc.Server
		if tracing.IsTracingEnabled() {
			grpcServer = tracing.GetGRPCServerWithUnaryInterceptor()
		} else {
			grpcServer = grpc.NewServer()
		}
		cs := consumerServer{transferType: transferType, XDTconfig: utils.ReadConfig(), storageBackend: storageBackend}
		pb.RegisterProducerConsumerServer(grpcServer, &cs)
		us := ubenchServer{transferType: transferType, XDTconfig: utils.ReadConfig(), storageBackend: storageBackend}
		pb_client.RegisterProdConDriverServer(grpcServer, &us)

		if err := grpcServer.Serve(lis); err != nil {
			log.Fatalf("[consumer] failed to serve: %s", err)
		}
	}
}
