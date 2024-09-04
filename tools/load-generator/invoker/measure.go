package main

import (
	// "context"
	"sync"
	"time"

	// "github.com/golang/protobuf/ptypes/empty"
	// log "github.com/sirupsen/logrus"
	// "go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc"
	"google.golang.org/grpc"
	// "google.golang.org/grpc/credentials/insecure"

	"github.com/vhive-serverless/vSwarm/tools/benchmarking_eventing/proto"

	// "github.com/vhive-serverless/vSwarm/tools/endpoint"
)

var (
	tsdbConn   *grpc.ClientConn
	tsdbClient proto.TimeseriesClient
	lock       sync.Mutex
)

func Start() {
	lock.Lock()
	defer lock.Unlock()
	return
}

func End() (durations []time.Duration) {
	lock.Lock()
	defer lock.Unlock()
	return
}
