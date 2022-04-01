package grpcclient

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"

	log "github.com/sirupsen/logrus"
	"google.golang.org/grpc"
)

// Base functionality ==============================================

// ------ gRPC Client interface ------
// Every client must implement this interface
type GrpcClient interface {
	Init(ip, port string)
	Request(req string) string
	Close()
}

// The base of the client
type ClientBase struct {
	address string
	port    string
	ctx     context.Context
	conn    *grpc.ClientConn
}

func (c *ClientBase) Connect(ip, port string) {
	// Connect to the given address
	address := fmt.Sprintf("%s:%s", ip, port)
	log.Printf("Connect to %s", address)
	conn, err := grpc.Dial(address, grpc.WithInsecure(), grpc.WithBlock())
	if err != nil {
		log.Fatalf("did not connect: %v", err)
	}
	c.conn = conn

	// Create a new context.
	// Permit 60 min timeout
	// The context is used all the time while the connection is established
	timeout := time.Minute * 60
	ctx, _ := context.WithTimeout(context.Background(), timeout)
	c.ctx = ctx
}

func (c *ClientBase) Close() {
	c.conn.Close()
}

func getMethodPayload(req string) (method int, payload string) {
	payload = req
	// In case we have specified the exact request we want in the string extract the info
	str := strings.SplitN(req, "|", 2)
	if len(str) == 2 {
		method, _ = strconv.Atoi(strings.ReplaceAll(str[0], " ", ""))
		payload = strings.ReplaceAll(str[1], " ", "")
	}
	return
}
