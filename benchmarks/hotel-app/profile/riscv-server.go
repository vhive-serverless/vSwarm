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
	// "sort"
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

	pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/profile"
	// tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"
)

// Server implements the geo service
type Server struct {
	pb.UnimplementedProfileServer
	CassandraSession *gocql.Session
	Port             int
	IpAddr           string
	MemcClient   *memcache.Client

}
type pfPlan struct {
	HotelID			string `cql:"hotelid"`
	Name			string `cql:"name"`
	PhoneNumber		string `cql:"phone_number"`
	Description		string `cql:"description"`
	StreetNumber	string `cql:"street_number"`
	StreetName		string `cql:"street_name"`
	City			string `cql:"city"`
	State			string `cql:"state"`
	Country			string `cql:"country"`	
	PostalCode		string `cql:"postal_code"`
	Lat				float64 `cql:"lat"`
	Lon				float64 `cql:"lon"`
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
	pb.RegisterProfileServer(srv, s)

	// Register reflection service on gRPC server.
	reflection.Register(srv)

	// listener
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	log.Printf("Start Profile server. Addr: %s:%d\n", s.IpAddr, s.Port)
	return srv.Serve(lis)
}
// message Hotel {
// 	string hotelid = 1;
// 	string name = 2;
// 	string phoneNumber = 3;
// 	string description = 4;
// 	Address address = 5;
// 	repeated Image images = 6;
//   }
  
//   message Address {
// 	string streetNumber = 1;
// 	string streetName = 2;
// 	string city = 3;
// 	string state = 4;
// 	string country = 5;
// 	string postalCode = 6;
// 	float lat = 7;
// 	float lon = 8;
//   }

// GetProfiles returns hotel profiles for requested IDs
func (s *Server) GetProfiles(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	

	res := new(pb.Result)
	hotels := make([]*pb.Hotel, 0)
	session:= s.CassandraSession

	// one hotel should only have one profile
	for _, hotelID := range req.HotelIds {
		// first check memcached
		keyspace := "profile_db"
		table := "profile"

		item, err := s.MemcClient.Get(hotelID)

		if item != nil {
			profile_strs := strings.Split(string(item.Value), "\n")
			for _, profile_str := range profile_strs {
				if len(profile_str) != 0 {
					profile_p := new(pb.Hotel)
					if err = json.Unmarshal(item.Value, profile_p); err != nil {
						log.Warn(err)
					}
					hotels = append(hotels, profile_p)
				}
			}
			fmt.Printf("Hotels in cache hits %+v\n", hotels)
		} else if err == memcache.ErrCacheMiss {
			fmt.Printf("Memcached miss\n")
			// memcached miss, set up mongo connection
			memc_str := ""
			// hotelPl := new(pfPlan)
			var hotelId string
			var name string
			var phoneNumber string
			var description string
			var streetNumber string
			var streetName string
			var city string
			var state string
			var country string
			var postalCode string
			var lat float64
			var lon float64

			// hotelPl := &pfPlan{}
			// var hotelPl pfPlan
			resultQ := session.Query("SELECT hotelid , name , phone_number, description, street_number , street_name, city, state, country, postal_code, lat, lon FROM " + keyspace + "." + table +" WHERE hotelid = ?", hotelID).Iter()
			if resultQ.NumRows() == 0 {
				fmt.Printf("No hotel found for hotelID = %s\n", hotelID)
				continue
			}
			
			resultQ.Scan(&hotelId, &name, &phoneNumber, &description, &streetNumber, &streetName, &city, &state, &country, &postalCode, &lat, &lon)
			
			address  := new(pb.Address)
			// res := new(pb.Result)
			address.StreetNumber = streetNumber
			address.StreetName = streetName
			address.City = city
			address.State = state
			address.Country = country
			address.PostalCode = postalCode
			address.Lat = float32(lat)
			address.Lon = float32(lon)

			fmt.Printf("address in cache miss : StreetNumber = %s, StreetName = %s, City = %s, State = %s, Country = %s, PostalCode = %s, Lat = %f, Lon = %f\n", address.StreetNumber, address.StreetName, address.City, address.State, address.Country, address.PostalCode, address.Lat, address.Lon)
			hotel_prof := &pb.Hotel{
				Id:          hotelId,
				Name:        name,
				PhoneNumber:  phoneNumber,
				Description: description,
				Address:     address,
			}
			hotels = append(hotels, hotel_prof)
			prof_json, err := json.Marshal(hotel_prof)
			if err != nil {
				fmt.Printf("json.Marshal err = %s\n", err)
			}
			memc_str += string(prof_json) + "\n"
				// }
			
			// write to memcached
			err = s.MemcClient.Set(&memcache.Item{Key: hotelID, Value: []byte(memc_str)})
			if err != nil {
				log.Warn("MMC error: ", err)
			}

			
		} else {
			fmt.Printf("Memmcached error = %s\n", err)
			panic(err)
		}
	}
	// sort.Sort(hotels)

	res.Hotels = hotels
	// fmt.Printf("In GetProfiles after getting resp\n")
	return res, nil
}
