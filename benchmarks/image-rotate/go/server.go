// MIT License

// Copyright (c) 2024 EASE lab

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
	"io"
	"net"
	"os"
	"time"

	"github.com/disintegration/imaging"
	log "github.com/sirupsen/logrus"
	pb "github.com/vhive-serverless/vSwarm-proto/proto/image_rotate"
	tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/reflection"
	"google.golang.org/grpc/status"

	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/gridfs"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var (
	zipkin           = flag.String("zipkin", "http://localhost:9411/api/v2/spans", "zipkin url")
	address          = flag.String("addr", "0.0.0.0:50051", "Address:Port the grpc server is listening to")
	default_image    = flag.String("default-image", "default.jpg", "Default image to be rotated if empty")
	database_address = flag.String("db_addr", "mongodb://image-rotate-database:27017", "Address of the data-base server")
	connection_mode  = flag.String("connection_mode", perInvocationMode, "MongoDB client lifecycle: per-invocation or persistent")
	mongo_timeout    = flag.Duration("mongo_timeout", 2*time.Second, "MongoDB connect, server selection, and socket timeout")
)

const (
	perInvocationMode = "per-invocation"
	persistentMode    = "persistent"
)

const dbName = "image_db"

func connectMongo(ctx context.Context, address string, timeout time.Duration) (*mongo.Client, *gridfs.Bucket, error) {
	clientOptions := options.Client().
		ApplyURI(address).
		SetConnectTimeout(timeout).
		SetServerSelectionTimeout(timeout).
		SetSocketTimeout(timeout)
	client, err := mongo.Connect(ctx, clientOptions)
	if err != nil {
		return nil, nil, fmt.Errorf("connect to MongoDB: %w", err)
	}
	fail := func(err error) (*mongo.Client, *gridfs.Bucket, error) {
		disconnectCtx, cancel := context.WithTimeout(context.Background(), timeout)
		defer cancel()
		_ = client.Disconnect(disconnectCtx)
		return nil, nil, err
	}
	if err := client.Ping(ctx, nil); err != nil {
		return fail(fmt.Errorf("ping MongoDB: %w", err))
	}
	bucket, err := gridfs.NewBucket(client.Database(dbName))
	if err != nil {
		return fail(fmt.Errorf("create GridFS bucket: %w", err))
	}
	return client, bucket, nil
}

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
	databaseAddress  string
	connectionMode   string
	mongoTimeout     time.Duration
	persistentClient *mongo.Client
	persistentBucket *gridfs.Bucket
}

func (s *server) bucketForInvocation(ctx context.Context) (*gridfs.Bucket, int64, func(), error) {
	if s.connectionMode == persistentMode {
		return s.persistentBucket, 0, func() {}, nil
	}

	started := time.Now()
	setupCtx, cancel := context.WithTimeout(ctx, s.mongoTimeout)
	defer cancel()
	client, bucket, err := connectMongo(setupCtx, s.databaseAddress, s.mongoTimeout)
	if err != nil {
		return nil, 0, nil, err
	}
	setupUS := time.Since(started).Microseconds()
	cleanup := func() {
		disconnectCtx, disconnectCancel := context.WithTimeout(context.Background(), s.mongoTimeout)
		defer disconnectCancel()
		if err := client.Disconnect(disconnectCtx); err != nil {
			log.Warnf("Error disconnecting from MongoDB: %v", err)
		}
	}
	return bucket, setupUS, cleanup, nil
}

func (s *server) RotateImage(ctx context.Context, in *pb.SendImage) (*pb.GetRotatedImage, error) {
	bucket, mongoSetupUS, cleanup, err := s.bucketForInvocation(ctx)
	if err != nil {
		return nil, status.Errorf(codes.Unavailable, "MongoDB setup failed: %v", err)
	}
	defer cleanup()

	var imgPath string
	var imgOutPath string
	if in.GetName() == "" {
		imgPath = *default_image
	} else {
		imgPath = in.GetName()
	}

	if _, err := os.Stat(imgPath); err != nil {
		inputImageFile, err := os.Create(imgPath)
		if err != nil {
			return nil, status.Errorf(codes.Internal, "create input image: %v", err)
		}
		downloadStream, err := bucket.OpenDownloadStreamByName(imgPath)
		if err != nil {
			_ = inputImageFile.Close()
			_ = os.Remove(imgPath)
			return nil, status.Errorf(codes.NotFound, "open GridFS image %q: %v", imgPath, err)
		}
		_, copyErr := io.Copy(inputImageFile, downloadStream)
		streamCloseErr := downloadStream.Close()
		fileCloseErr := inputImageFile.Close()
		if copyErr != nil || streamCloseErr != nil || fileCloseErr != nil {
			_ = os.Remove(imgPath)
			return nil, status.Errorf(
				codes.Internal,
				"download GridFS image %q: copy=%v stream_close=%v file_close=%v",
				imgPath,
				copyErr,
				streamCloseErr,
				fileCloseErr,
			)
		}
	}

	imgOutPath = "rotated_" + imgPath
	message := imageRotate(imgPath, imgOutPath)
	resp := fmt.Sprintf(
		"fn: ImageRotate | image: %s | return msg: %s | runtime: Go | connection_mode: %s | mongo_setup_us: %d",
		imgPath,
		message,
		s.connectionMode,
		mongoSetupUS,
	)
	return &pb.GetRotatedImage{Message: resp}, nil
}

func main() {

	flag.Parse()
	if *connection_mode != perInvocationMode && *connection_mode != persistentMode {
		log.Fatalf("Unsupported MongoDB connection mode %q", *connection_mode)
	}
	if *mongo_timeout <= 0 {
		log.Fatalf("MongoDB timeout must be positive")
	}
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

	functionServer := &server{
		databaseAddress: *database_address,
		connectionMode:  *connection_mode,
		mongoTimeout:    *mongo_timeout,
	}
	if functionServer.connectionMode == persistentMode {
		setupCtx, cancel := context.WithTimeout(context.Background(), functionServer.mongoTimeout)
		client, bucket, err := connectMongo(setupCtx, functionServer.databaseAddress, functionServer.mongoTimeout)
		cancel()
		if err != nil {
			log.Fatalf("Error connecting to MongoDB: %v", err)
		}
		functionServer.persistentClient = client
		functionServer.persistentBucket = bucket
		defer func() {
			disconnectCtx, disconnectCancel := context.WithTimeout(context.Background(), functionServer.mongoTimeout)
			defer disconnectCancel()
			if err := client.Disconnect(disconnectCtx); err != nil {
				log.Warnf("Disconnect error: %v", err)
			}
		}()
	}

	log.Printf("Start ImageRotate-go server. Addr: %s\n", *address)
	var grpcServer *grpc.Server
	if tracing.IsTracingEnabled() {
		grpcServer = tracing.GetGRPCServerWithUnaryInterceptor()
	} else {
		grpcServer = grpc.NewServer()
	}
	pb.RegisterImageRotateServer(grpcServer, functionServer)
	reflection.Register(grpcServer)
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
