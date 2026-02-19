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
	"fmt"

	"net"

	log "github.com/sirupsen/logrus"

	"time"

	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/reflection"

	geo "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/geo"
	rate "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/rate"

	pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/search"

	tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"
)

// Server implments the search service
type Server struct {
	pb.UnimplementedSearchServer

	geoClient  geo.GeoClient
	rateClient rate.RateClient
	GeoAddr    string
	RateAddr   string

	Port   int
	IpAddr string
}

// Run starts the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}

	opts := []grpc.ServerOption{
		grpc.KeepaliveParams(keepalive.ServerParameters{
			Timeout: 120 * time.Second,
		}),
		grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
			PermitWithoutStream: true,
		}),
	}

	if tracing.IsTracingEnabled() {
		opts = append(opts, tracing.GetServerInterceptor())
	}

	// if tlsopt := tls.GetServerOpt(); tlsopt != nil {
	// 	opts = append(opts, tlsopt)
	// }

	srv := grpc.NewServer(opts...)
	pb.RegisterSearchServer(srv, s)

	// Register reflection service on gRPC server.
	reflection.Register(srv)

	// init grpc clients
	if err := s.initGeoClient(); err != nil {
		return err
	}
	if err := s.initRateClient(); err != nil {
		return err
	}

	// listener
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	log.Printf("Start Search server. Addr: %s:%d\n", s.IpAddr, s.Port)
	return srv.Serve(lis)
}

// Dial returns a load balanced grpc client conn with tracing interceptor
func dial(address string) (*grpc.ClientConn, error) {

	dialopts := []grpc.DialOption{
		grpc.WithKeepaliveParams(keepalive.ClientParameters{
			Timeout:             120 * time.Second,
			PermitWithoutStream: true,
		}),
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	}

	if tracing.IsTracingEnabled() {
		dialopts = append(dialopts, tracing.GetClientInterceptor())
	}

	log.Printf("Connect to %s", address)
	return grpc.NewClient(address, dialopts...)
}

func (s *Server) initGeoClient() error {

	conn, err := dial(s.GeoAddr)
	if err != nil {
		return fmt.Errorf("did not connect to geo service: %v", err)
	}
	s.geoClient = geo.NewGeoClient(conn)
	return nil
}

func (s *Server) initRateClient() error {
	conn, err := dial(s.RateAddr)
	if err != nil {
		return fmt.Errorf("did not connect to rate service: %v", err)
	}
	s.rateClient = rate.NewRateClient(conn)
	return nil
}

// Nearby returns ids of nearby hotels ordered by ranking algo
func (s *Server) Nearby(ctx context.Context, req *pb.NearbyRequest) (*pb.SearchResult, error) {
	// find nearby hotels
	fmt.Printf("in Search Nearby\n")

	fmt.Printf("nearby lat = %f\n", req.Lat)
	fmt.Printf("nearby lon = %f\n", req.Lon)

	nearby, err := s.geoClient.Nearby(ctx, &geo.Request{
		Lat: req.Lat,
		Lon: req.Lon,
	})

	if err != nil {
		fmt.Printf("nearby error: %v", err)
		return nil, err
	}

	// var ids []string
	for _, hid := range nearby.HotelIds {
		fmt.Printf("get Nearby hotelId = %s\n", hid)
		// ids = append(ids, hid)
	}

	// find rates for hotels
	r := rate.Request{
		HotelIds: nearby.HotelIds,
		// HotelIds: []string{"2"},
		InDate:  req.InDate,
		OutDate: req.OutDate,
	}

	rates, err := s.rateClient.GetRates(ctx, &r)
	if err != nil {
		fmt.Printf("rates error: %v", err)
		return nil, err
	}

	// TODO(hw): add simple ranking algo to order hotel ids:
	// * geo distance
	// * price (best discount?)
	// * reviews

	// build the response
	res := new(pb.SearchResult)
	for _, ratePlan := range rates.RatePlans {
		// fmt.Printf("get RatePlan HotelId = %s, Code = %s\n", ratePlan.HotelId, ratePlan.Code)
		res.HotelIds = append(res.HotelIds, ratePlan.HotelId)
	}
	return res, nil
}
