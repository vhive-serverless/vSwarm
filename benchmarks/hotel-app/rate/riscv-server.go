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
	"encoding/json"
	"fmt"
	"sort"
	"strings"

	// "gopkg.in/mgo.v2"
	// "gopkg.in/mgo.v2/bson"

	"net"

	log "github.com/sirupsen/logrus"

	"time"

	"github.com/bradfitz/gomemcache/memcache"
	"github.com/gocql/gocql"

	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/reflection"

	pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/rate"
	// tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"
)


type Server struct {
	pb.UnimplementedRateServer
	CassandraSession *gocql.Session
	Port             int
	IpAddr           string
	MemcClient   *memcache.Client

}
// type Point struct {
// 	Pid  string  `cql:"hotelid"`
// 	Plat float64 `cql:"lat"`
// 	Plon float64 `cql:"lon"`
// }
type rtPlan struct {
	HotelID            string `cql:"hotelid"`
	Code               string `cql:"code"`
	Indate             string `cql:"indate"`
	Outdate            string `cql:"outdate"`
	BookableRate       float64 `cql:"bookablerate"`
	TotalRate          float64 `cql:"totalrate"`
	TotalRateInclusive float64 `cql:"totalrateinclusive"`
	RoomCode           string `cql:"roomcode"`
	RoomDescription    string `cql:"roomdescription"`
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

	// if tracing.IsTracingEnabled() {
	// 	opts = append(opts, tracing.GetServerInterceptor())
	// }

	srv := grpc.NewServer(opts...)
	pb.RegisterRateServer(srv, s)

	// Register reflection service on gRPC server.
	reflection.Register(srv)

	// listener
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	log.Printf("Start Rate server. Addr: %s:%d\n", s.IpAddr, s.Port)
	return srv.Serve(lis)
}


// GetRates gets rates for hotels for specific date range.
func (s *Server) GetRates(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	res := new(pb.Result)
	
	session:= s.CassandraSession
	ratePlans := make(RatePlans, 0)


	for _, hotelID := range req.HotelIds {
		// first check memcached
		keyspace := "rate_db"
		table := "rate"
		item, err := s.MemcClient.Get(hotelID)
		if err == nil {
			// memcached hit
			rate_strs := strings.Split(string(item.Value), "\n")

			// fmt.Printf("memc hit, hotelId = %s\n", hotelID)
			fmt.Println(rate_strs)

			for _, rate_str := range rate_strs {
				if len(rate_str) != 0 {
					rate_p := new(pb.RatePlan)
					if err = json.Unmarshal(item.Value, rate_p); err != nil {
						log.Warn(err)
					}
					ratePlans = append(ratePlans, rate_p)
				}
			}
		} else if err == memcache.ErrCacheMiss {

			// fmt.Printf("memc miss, hotelId = %s\n", hotelID)

			
			memc_str := ""
			
			// tmpRatePlans := make(RatePlans, 0)
			fmt.Printf("about to ask for hotelid = %s\n", hotelID)	

			resultQ := session.Query("SELECT hotelid ,code,indate,outdate, bookablerate, totalrate,totalrateinclusive, roomdescription , roomcode FROM " + keyspace + "." + table +" WHERE hotelid = ?", hotelID).Iter()
			
			if resultQ.NumRows() == 0 {
				fmt.Printf("No rate found for hotelID = %s\n", hotelID)
				continue
			}
			for {
				var hotelID string
				var code string
				var indate string
				var outdate string
				var bookablerate float64
				var totalrate float64
				var totalrateinclusive float64
				var roomdescription string
				var roomcode string
				if !resultQ.Scan(&hotelID, &code, &indate, &outdate, &bookablerate, &totalrate, &totalrateinclusive, &roomdescription, &roomcode){break}
				
				RoomType := &pb.RoomType{
					BookableRate: bookablerate,
					TotalRate: totalrate,
					TotalRateInclusive: totalrateinclusive,
					Code: roomcode,
					RoomDescription: roomdescription,
				}
				r := &pb.RatePlan{
					HotelId: hotelID,
					Code: code,
					InDate: indate,
					OutDate: outdate,
					RoomType: RoomType,
				}
				
				ratePlans = append(ratePlans, r)
				rate_json, err := json.Marshal(r)
				if err != nil {
					fmt.Printf("json.Marshal err = %s\n", err)
				}
				memc_str = memc_str + string(rate_json) + "\n"
			}
			
			err = s.MemcClient.Set(&memcache.Item{Key: hotelID, Value: []byte(memc_str)})
			if err != nil {
				log.Warn("MMC error: ", err)
			}
		} else {
			fmt.Printf("Memmcached error = %s\n", err)
			panic(err)
		}
	}

	sort.Sort(ratePlans)
	res.RatePlans = ratePlans

	return res, nil
}

type RatePlans []*pb.RatePlan


func (r RatePlans) Len() int {
	return len(r)
}

func (r RatePlans) Swap(i, j int) {
	r[i], r[j] = r[j], r[i]
}

func (r RatePlans) Less(i, j int) bool {
	return r[i].RoomType.TotalRate > r[j].RoomType.TotalRate
}
