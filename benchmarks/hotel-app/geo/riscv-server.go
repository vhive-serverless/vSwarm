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
	"fmt"
	"log"
	"net"
	"time"

	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/reflection"
	// "gopkg.in/mgo.v2"

	"github.com/gocql/gocql"

	"github.com/hailocab/go-geoindex"

	pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/geo"
)

const (
	maxSearchRadius  = 10
	maxSearchResults = 5
)



type Server struct {
	pb.UnimplementedGeoServer
	index            *geoindex.ClusteringIndex
	CassandraSession *gocql.Session
	Port             int
	IpAddr           string
}

// Run starts the server

func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}

	if s.index == nil {
		s.index = newCassandraGeoIndex(s.CassandraSession)
	}

	opts := []grpc.ServerOption{
		grpc.KeepaliveParams(keepalive.ServerParameters{
			Timeout: 120 * time.Second,
		}),
		grpc.KeepaliveEnforcementPolicy(keepalive.EnforcementPolicy{
			PermitWithoutStream: true,
		}),
	}


	srv := grpc.NewServer(opts...)

	pb.RegisterGeoServer(srv, s)

	// Register reflection service on gRPC server.
	reflection.Register(srv)

	// listener
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	log.Printf("Start Geo server. Addr: %s:%d\n", s.IpAddr, s.Port)
	return srv.Serve(lis)
}

// newGeoIndex returns a geo index with points loaded

func newCassandraGeoIndex(session *gocql.Session) *geoindex.ClusteringIndex {

	keyspace := "geo_db"
	table := "geo"

	// Query for all rows in the "geo" table
	var points []*Point
	query := session.Query("SELECT * FROM " + keyspace + "." + table)
	iter := query.Iter()
	for {
		var point Point
		if !iter.Scan(&point.Pid, &point.Plat, &point.Plon) {
			break
		}

		points = append(points, &point)

	}
	// Check for errors during the iteration
	if err := iter.Close(); err != nil {
		log.Println("Failed to iterate over geo data: ", err)
	}

	fmt.Printf("newGeoIndex len(points) = %d\n", len(points))

	// add points to index
	index := geoindex.NewClusteringIndex()
	for _, point := range points {
		index.Add(point)

	}

	return index
}

func (s *Server) Nearby(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	// fmt.Printf("In geo Nearby\n")

	var (
		points = s.getNearbyPoints(ctx, float64(req.Lat), float64(req.Lon))
		res    = &pb.Result{}
	)

	// fmt.Printf("geo after getNearbyPoints, len = %d\n", len(points))

	for _, p := range points {
		// fmt.Printf("In geo Nearby return hotelId = %s\n", p.Id())
		res.HotelIds = append(res.HotelIds, p.Id())
	}

	return res, nil
}

func (s *Server) getNearbyPoints(ctx context.Context, lat, lon float64) []geoindex.Point {
	// fmt.Printf("In geo getNearbyPoints, lat = %f, lon = %f\n", lat, lon)

	center := &geoindex.GeoPoint{
		Pid:  "",
		Plat: lat,
		Plon: lon,
	}

	return s.index.KNearest(
		center,
		maxSearchResults,
		geoindex.Km(maxSearchRadius), func(p geoindex.Point) bool {
			return true
		},
	)
}

type Point struct {
	Pid  string  `cql:"hotelid"`
	Plat float64 `cql:"lat"`
	Plon float64 `cql:"lon"`
}

// Implement Point interface
func (p *Point) Lat() float64 { return p.Plat }
func (p *Point) Lon() float64 { return p.Plon }
func (p *Point) Id() string   { return p.Pid }

