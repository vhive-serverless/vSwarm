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
// type HotelDB struct {
// 	HId    string  `bson:"hotelid"`
// 	HLat   float64 `bson:"lat"`
// 	HLon   float64 `bson:"lon"`
// 	HRate  float64 `bson:"rate"`
// 	HPrice float64 `bson:"price"`
// }

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
	fmt.Println("Keyspace " + keyspaceName + " created successfully.")
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
	tableName := action
	ExecuteQuery(connection.session, "DROP TABLE IF EXISTS "+tableName)
	cqlCreateTable := `
		CREATE TABLE IF NOT EXISTS ` + tableName + `( hotelid text, lat double , lon double , rate double , price double, PRIMARY KEY (hotelid));`
	ExecuteQuery(connection.session, cqlCreateTable)
	var hotelIdExists int64
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = '1'").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, lat, lon, rate, price) VALUES ('1', 37.7867, -122.4112, 109.00, 150.00)")
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = '2'").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, lat, lon, rate, price) VALUES ('2', 37.7854, -122.4005, 139.00, 120.00)")
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = '3'").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, lat, lon, rate, price) VALUES ('3', 37.7834, -122.4071, 109.00, 190.00)")
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = '4'").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, lat, lon, rate, price) VALUES ('4', 37.7936, -122.3930, 129.00, 160.00)")
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = '5'").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, lat, lon, rate, price) VALUES ('5', 37.7831, -122.4181, 119.00, 140.00)")
	}
	err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = '6'").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, lat, lon, rate, price) VALUES ('6', 37.7863, -122.4015, 149.00, 200.00)")
	}
	for i := 7; i <= 80; i++ {
		hotel_id := strconv.Itoa(i)
		err = connection.session.Query("SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = '"+hotel_id+"'").Scan(&hotelIdExists)
		if err != nil {
			log.Fatal(err)
		}
		if hotelIdExists == 0 {
			lat := 37.7835 + float64(i)/500.0*3
			lon := -122.41 + float64(i)/500.0*4
			rate := 135.00
			price := 179.00
			if i%3 == 0 {
				if i%5 == 0 {
					rate = 109.00
					price = 123.17
				} else if i%5 == 1 {
					rate = 120.00
					price = 140.00
				} else if i%5 == 2 {
					rate = 124.00
					price = 144.00
				} else if i%5 == 3 {
					rate = 132.00
					price = 158.00
				} else if i%5 == 4 {
					rate = 232.00
					price = 258.00
				}
			}
			ExecuteQuery(connection.session, "INSERT INTO "+tableName+" (hotelid, lat, lon, rate, price) VALUES (? , ? , ? , ? , ?)", hotel_id, lat, lon, rate, price)
		}
	}
		
	
	fmt.Println("Just when I thought I was out, they pull me back in")
	return connection.session
	
}
