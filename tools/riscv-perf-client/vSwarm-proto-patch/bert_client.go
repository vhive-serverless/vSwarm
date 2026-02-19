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
package grpcclient

import (
	"context"
	"fmt"

	// log "github.com/sirupsen/logrus"
	pb "github.com/vhive-serverless/vSwarm-proto/proto/bert"
)

type BertGenerator struct {
	GeneratorBase
}

func (g *BertGenerator) Next() Input {
	var pkt = g.defaultInput
	switch g.GeneratorBase.generator {
	case Unique:
		pkt.Value = "A unique message"
	case Linear:
		pkt.Value = "A linear message"
	case Random:
		pkt.Value = "random"
	}
	return pkt
}

func (c *BertClient) GetGenerator() Generator {
	return new(BertGenerator)
}

type BertClient struct {
	ClientBase
	client pb.GreeterClient
}

func (c *BertClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewGreeterClient(c.conn)
	return nil

}

func (c *BertClient) Request(ctx context.Context, req Input) (string, error) {
	var bertMessage = req.Value
	r, err := c.client.SayHello(ctx, &pb.HelloRequest{Name: bertMessage})
	if err != nil {
		// log.Fatalf("could not greet: %v", err)
		return "", err
	}
	msg := fmt.Sprintf("inference time in ns: max: %d; min: %d; mean: %d", r.GetMaxLatency(),r.GetMinLatency(),r.GetMeanLatency())
	return msg , nil
}
