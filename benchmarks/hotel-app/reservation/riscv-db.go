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
	"log"
	"strconv"
	"time"

	"github.com/gocql/gocql"

)
type DBConnection struct {
	cluster *gocql.ClusterConfig
	session *gocql.Session
}

func ExecuteQuery(session *gocql.Session, query string, values ...interface{}) {
	if err := session.Query(query).Bind(values...).Exec(); err != nil {
		log.Fatal(err)
	}
}
func initializeCassandraDatabase(url string, action string) *gocql.Session {
	var connection DBConnection
	fmt.Printf(action+" db ip addr = %s\n", url)
	connection.cluster = gocql.NewCluster(url)
	connection.cluster.Keyspace = "system" // Use the "system" keyspace to create your keyspace
	connection.cluster.Consistency = gocql.Quorum
	connection.cluster.ConnectTimeout = 20 * time.Second // ConnectTimeout set to 2 seconds
	connection.cluster.Timeout = 50 * time.Second        // Timeout set to 5 seconds
	var err error
	for {
		connection.session, err = connection.cluster.CreateSession()
		if err == nil {
			break
		}
		log.Printf("CreateSession: %v", err)
		time.Sleep(15*time.Second)
	}
	
	keyspaceName := action + "_db"
	err = connection.session.Query(`
		CREATE KEYSPACE IF NOT EXISTS ` + keyspaceName + ` 
		WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
	`).Exec()
	if err != nil {
		log.Fatal(err)
	}
	connection.cluster.Keyspace = keyspaceName
	log.Printf("Connected OK")
	for {
		connection.session, err = connection.cluster.CreateSession()
		if err == nil {
			break
		}
		log.Printf("CreateSession: %v", err)
		time.Sleep(15*time.Second)
	}
	fmt.Println("Keyspace " + keyspaceName + " created successfully.")
	log.Printf("Connected OK2")
	tableName := action
	ExecuteQuery(connection.session, "DROP TABLE IF EXISTS "+tableName)
	createTableQuery := "CREATE TABLE " + tableName + " (hotelid text , name text, checkin text, checkout text, roomnum int , PRIMARY KEY (hotelid))"
	
	ExecuteQuery(connection.session, createTableQuery)
	var hotelIdExists int64
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "4").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, name, checkin, checkout, roomnum) VALUES (?, ?, ?, ?, ?)", "4", "Alice", "2015-04-09", "2015-04-10", 1)
	}
	tableName = "number"
	ExecuteQuery(connection.session, "DROP TABLE IF EXISTS "+tableName)
	createTableQuery = "CREATE TABLE " + tableName + " (hotelid text , roomnum int , PRIMARY KEY (hotelid))"
	
	ExecuteQuery(connection.session, createTableQuery)
	// var hotelIdExists int64
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "1").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, roomnum) VALUES (?, ?)", "1", 200)
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "2").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, roomnum) VALUES (?, ?)", "2", 10)
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "3").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, roomnum) VALUES (?, ?)", "3", 200)
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "4").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, roomnum) VALUES (?, ?)", "4", 200)
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "5").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, roomnum) VALUES (?, ?)", "5", 200)
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "6").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, roomnum) VALUES (?, ?)", "6", 200)
	}
	for i := 7; i <= 80; i++ {
		hotel_id := strconv.Itoa(i)
		err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", hotel_id).Scan(&hotelIdExists)
		if err != nil {
			log.Fatal(err)
		}
		room_num := 200
		if i%3 == 1 {
			room_num = 300
		} else if i%3 == 2 {
			room_num = 250
		}
		if hotelIdExists == 0 {
			ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, roomnum) VALUES (?, ?)", hotel_id, room_num)
		}
	}
	fmt.Println("Just when I thought I was out, they pull me back in")

	return connection.session
}

