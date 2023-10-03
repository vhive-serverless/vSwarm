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
	"crypto/rand"
	"flag"
	"fmt"
	"net"
	"os"
	"strconv"

	storage "github.com/vhive-serverless/vSwarm/utils/storage/go"

	sdk "github.com/ease-lab/vhive-xdt/sdk/golang"
	"github.com/ease-lab/vhive-xdt/utils"
	"google.golang.org/grpc/credentials/insecure"

	ctrdlog "github.com/containerd/containerd/log"
	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc/reflection"

	pb_client "tests/chained-functions-serving/proto"

	pb "github.com/vhive-serverless/vSwarm/examples/protobuf/helloworld"
	"google.golang.org/grpc"

	tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"
)

type producerServer struct {
	consumerAddr   string
	consumerPort   int
	payloadData    []byte
	XDTclient      *sdk.XDTclient
	transferType   string
	randomStr      string
	storageBackend storage.Storage
	pb.UnimplementedGreeterServer
}

type ubenchServer struct {
	consumerAddr   string
	consumerPort   int
	transferType   string
	payloadData    []byte
	XDTclient      *sdk.XDTclient
	randomStr      string
	storageBackend storage.Storage
	pb_client.UnimplementedProdConDriverServer
}

const (
	INLINE      = "INLINE"
	XDT         = "XDT"
	S3          = "S3"
	ELASTICACHE = "ELASTICACHE"
)

func uploadToStorage(ctx context.Context, payloadData []byte, randomStr string, storageBackend storage.Storage) string {
	span := tracing.Span{SpanName: "Storage put", TracerName: "Storage put - tracer"}
	span.StartSpan(ctx)
	defer span.EndSpan()

	key := fmt.Sprintf("payload_bytes_%s.txt", randomStr)
	key = storageBackend.Put(ctx, key, payloadData)
	log.Infof("[producer] Successfully uploaded %q", key)
	return key
}
func getGRPCclient(addr string) (pb_client.ProducerConsumerClient, *grpc.ClientConn) {
	// establish a connection
	var conn *grpc.ClientConn
	var err error
	if tracing.IsTracingEnabled() {
		conn, err = tracing.DialGRPCWithUnaryInterceptor(addr, grpc.WithBlock(), grpc.WithTransportCredentials(insecure.NewCredentials()))
	} else {
		conn, err = grpc.Dial(addr, grpc.WithBlock(), grpc.WithTransportCredentials(insecure.NewCredentials()))
	}
	if err != nil {
		log.Fatalf("[producer] fail to dial: %s", err)
	}
	return pb_client.NewProducerConsumerClient(conn), conn
}

func (ps *producerServer) SayHello(ctx context.Context, req *pb.HelloRequest) (_ *pb.HelloReply, err error) {
	addr := fmt.Sprintf("%v:%v", ps.consumerAddr, ps.consumerPort)
	if ps.transferType == INLINE || ps.transferType == S3 || ps.transferType == ELASTICACHE {
		client, conn := getGRPCclient(addr)
		defer conn.Close()
		payloadToSend := ps.payloadData
		if ps.transferType == S3 || ps.transferType == ELASTICACHE {
			payloadToSend = []byte(uploadToStorage(ctx, ps.payloadData, ps.randomStr, ps.storageBackend))
		}
		ack, err := client.ConsumeByte(ctx, &pb_client.ConsumeByteRequest{Value: payloadToSend})
		if err != nil {
			log.Fatalf("[producer] client error in string consumption: %s", err)
		}
		log.Printf("[producer] (single) Ack: %v\n", ack.Value)
	} else if ps.transferType == XDT {
		payloadToSend := utils.Payload{
			FunctionName: "HelloXDT",
			Data:         ps.payloadData,
		}
		if _, _, err := ps.XDTclient.Invoke(ctx, addr, payloadToSend); err != nil {
			log.Fatalf("SQP_to_dQP_data_transfer failed %v", err)
		}
	}
	return &pb.HelloReply{Message: "Success"}, err
}

func main() {
	flagAddress := flag.String("addr", "consumer.default.192.168.1.240.sslip.io", "Server IP address")
	flagClientPort := flag.Int("pc", 80, "Client Port")
	flagServerPort := flag.Int("ps", 80, "Server Port")
	url := flag.String("zipkin", "http://zipkin.istio-system.svc.cluster.local:9411/api/v2/spans", "zipkin url")
	dockerCompose := flag.Bool("dockerCompose", false, "Env docker Compose?")
	flag.Parse()

	log.SetFormatter(&log.TextFormatter{
		TimestampFormat: ctrdlog.RFC3339NanoFixed,
		FullTimestamp:   true,
	})
	log.SetOutput(os.Stdout)

	if tracing.IsTracingEnabled() {
		log.Println("producer has tracing enabled")
		shutdown, err := tracing.InitBasicTracer(*url, "producer")
		if err != nil {
			log.Warn(err)
		}
		defer shutdown()
	} else {
		log.Println("producer has tracing DISABLED")
	}

	var grpcServer *grpc.Server
	if tracing.IsTracingEnabled() {
		grpcServer = tracing.GetGRPCServerWithUnaryInterceptor()
	} else {
		grpcServer = grpc.NewServer()
	}

	//client setup
	log.Printf("[producer] Client using address: %v:%d\n", *flagAddress, *flagClientPort)

	ps := producerServer{consumerAddr: *flagAddress, consumerPort: *flagClientPort}
	us := ubenchServer{consumerAddr: *flagAddress, consumerPort: *flagClientPort}

	transferType, ok := os.LookupEnv("TRANSFER_TYPE")
	if !ok {
		log.Infof("TRANSFER_TYPE not found, using INLINE transfer")
		transferType = INLINE
	}
	log.Infof("[producer] transfering via %s", transferType)
	ps.transferType = transferType
	us.transferType = transferType

	transferSizeKB := 4095
	if value, ok := os.LookupEnv("TRANSFER_SIZE_KB"); ok {
		if intValue, err := strconv.Atoi(value); err == nil {
			transferSizeKB = intValue
		} else {
			log.Infof("invalid TRANSFER_SIZE_KB: %s, using default %d", value, transferSizeKB)
		}
	}

	// 4194304 bytes is the limit by gRPC
	payloadData := make([]byte, transferSizeKB*1024)
	if _, err := rand.Read(payloadData); err != nil {
		log.Fatal(err)
	}
	ps.randomStr = os.Getenv("HOSTNAME")
	us.randomStr = ps.randomStr

	log.Infof("sending %d bytes to consumer", len(payloadData))
	ps.payloadData = payloadData
	us.payloadData = payloadData
	if transferType == XDT {
		config := utils.ReadConfig()
		if !*dockerCompose {
			config.SQPServerHostname = utils.FetchSelfIP()
		}
		xdtClient, err := sdk.NewXDTclient(config)
		if err != nil {
			log.Fatalf("InitXDT failed %v", err)
		}

		ps.XDTclient = xdtClient

		us.XDTclient = xdtClient
	} else if transferType == S3 || transferType == ELASTICACHE {

		bucketName, ok := os.LookupEnv("BUCKET_NAME")
		if !ok {
			bucketName = "vhive-prodcon-bench"
		}
		storageBackend := storage.New(transferType, bucketName)
		us.storageBackend = storageBackend
		ps.storageBackend = storageBackend
	}
	pb.RegisterGreeterServer(grpcServer, &ps)
	pb_client.RegisterProdConDriverServer(grpcServer, &us)
	reflection.Register(grpcServer)

	//server setup
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", *flagServerPort))
	if err != nil {
		log.Fatalf("[producer] failed to listen: %v", err)
	}

	log.Println("[producer] Server Started")

	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("[producer] failed to serve: %s", err)
	}

}
