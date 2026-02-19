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

	// "go.mongodb.org/mongo-driver/bson"
	// "go.mongodb.org/mongo-driver/bson/primitive"
	// "go.mongodb.org/mongo-driver/mongo"

	"net"

	log "github.com/sirupsen/logrus"

	"time"

	"crypto/sha256"

	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/keepalive"
	"google.golang.org/grpc/reflection"
	"github.com/gocql/gocql"

	pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/user"
	// tracing "github.com/vhive-serverless/vSwarm/utils/tracing/go"
)

type User struct {
	Username string `cql:"username"`
	Password string `cql:"password"`
}

// Server implements the user service
type Server struct {
	pb.UnimplementedUserServer

	users_cached map[string]string

	Port        int
	IpAddr      string
	CassandraSession *gocql.Session
}

// Run starts the server
func (s *Server) Run() error {
	if s.Port == 0 {
		return fmt.Errorf("server port must be set")
	}
	if s.users_cached == nil {
		s.users_cached = loadUsers(s.CassandraSession)
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

	// Create the user server
	srv := grpc.NewServer(opts...)
	pb.RegisterUserServer(srv, s)

	// Register reflection service on gRPC server.
	reflection.Register(srv)

	// listener
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.Port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	log.Printf("Start User server. Addr: %s:%d\n", s.IpAddr, s.Port)
	return srv.Serve(lis)
}

// CheckUser returns whether the username and password are correct.
func (s *Server) CheckUser(ctx context.Context, req *pb.Request) (*pb.Result, error) {
	res := new(pb.Result)

	fmt.Printf("CheckUser: %+v", req)

	sum := sha256.Sum256([]byte(req.Password))
	pass := fmt.Sprintf("%x", sum)

	use_cache := false

	if use_cache {
		password := s.lookupCache(req.Username)
		res.Correct = pass == password
	} else {
		user, _ := s.lookUpDB(req.Username)
		res.Correct = pass == user.Password
	}

	fmt.Printf(" >> pass: %t\n", res.Correct)

	return res, nil
}

// loadUsers loads hotel users from database
func loadUsers(session *gocql.Session) map[string]string {

	keyspace := "user_db"
	table := "user"
	var usr User
	resultQ := session.Query("SELECT username , password FROM " + keyspace + "." + table ).Iter()
	if resultQ.NumRows() == 0 {
		panic("No users found in the database\n")
	}
	res := make(map[string]string)
	for resultQ.Scan(&usr.Username, &usr.Password) {
		res[usr.Username] = usr.Password
	}
	return res
}



func (s *Server) lookupCache(username string) string {
	res, ok := s.users_cached[username]
	if !ok {
		log.Println("User does not exist: ", username)
	}
	return res
}

//
func (s *Server) lookUpDB(username string) (User, bool) {
	
	keyspace := "user_db"
	table := "user"
	var usr User
	err:= s.CassandraSession.Query("SELECT * FROM " + keyspace + "." + table+" WHERE username = ?", username ).Scan(&usr.Username, &usr.Password)
	if err != nil {
		log.Println("Failed get user: ", err)
		return usr, false
	}
	
	return usr, true
}
