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
	"strconv"
	"time"

	"github.com/gocql/gocql"
	log "github.com/sirupsen/logrus"
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

	//
	err = connection.session.Query(`
		CREATE KEYSPACE IF NOT EXISTS ` + keyspaceName + ` 
		WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
	`).Exec()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println("Keyspace " + keyspaceName + " created successfully.")
	// connection.cluster.Keyspace = "geo-db"
	connection.cluster.Keyspace = keyspaceName
	log.Printf("Connected OK")
	for {
		connection.session, err = connection.cluster.CreateSession()
		if err == nil {
			break
		}
		log.Printf("CreateSession: %v", err)
		time.Sleep(15 * time.Second)
	}
	tableName := action
	ExecuteQuery(connection.session, "DROP TABLE IF EXISTS "+tableName)
	
	cqlCreateTable := `
    CREATE TABLE IF NOT EXISTS ` + tableName + `(
        hotelid text PRIMARY KEY,
        lat double,
        lon double
    )`

	// Execute the CQL query to create the table
	ExecuteQuery(connection.session, cqlCreateTable)
	var hotelIdExists int64
	err = connection.session.Query(`SELECT COUNT(*) FROM `+tableName+` WHERE hotelid = ?`, "1").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}

	// Insert a new row into the "geo" table
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `INSERT INTO geo (hotelid, lat, lon) VALUES (?, ?, ?)`, "1", 37.7867, -122.4112)
	}

	

	err = connection.session.Query(`SELECT COUNT(*) FROM geo WHERE hotelid = ?`, "2").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}

	if hotelIdExists == 0 {
		// Insert a new row into the "geo" table
		ExecuteQuery(connection.session, `INSERT INTO geo (hotelid, lat, lon) VALUES (?, ?, ?)`, "2", 37.7854, -122.4005)
		
	}
	err = connection.session.Query(`SELECT COUNT(*) FROM geo WHERE hotelid = ?`, "3").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}

	if hotelIdExists == 0 {
		// Insert a new row into the "geo" table
		ExecuteQuery(connection.session, `INSERT INTO geo (hotelid, lat, lon) VALUES (?, ?, ?)`, "3", 37.7854, -122.4071)
		
	}
	err = connection.session.Query(`SELECT COUNT(*) FROM geo WHERE hotelid = ?`, "4").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}

	if hotelIdExists == 0 {
		// Insert a new row into the "geo" table
		ExecuteQuery(connection.session, `INSERT INTO geo (hotelid, lat, lon) VALUES (?, ?, ?)`, "4", 37.7936, -122.3930)
		
	}
	err = connection.session.Query(`SELECT COUNT(*) FROM geo WHERE hotelid = ?`, "5").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}

	if hotelIdExists == 0 {
		// Insert a new row into the "geo" table
		ExecuteQuery(connection.session, `INSERT INTO geo (hotelid, lat, lon) VALUES (?, ?, ?)`, "5", 37.7831, -122.4181)
		
	}
	err = connection.session.Query(`SELECT COUNT(*) FROM geo WHERE hotelid = ?`, "6").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}

	if hotelIdExists == 0 {
		// Insert a new row into the "geo" table
		ExecuteQuery(connection.session, `INSERT INTO geo (hotelid, lat, lon) VALUES (?, ?, ?)`, "6", 37.7863, -122.4015)
		
	}
	for i := 7; i <= 80; i++ {
		hotelID := strconv.Itoa(i)
		err = connection.session.Query(`SELECT COUNT(*) FROM geo WHERE hotelid = ?`, hotelID).Scan(&hotelIdExists)
		if err != nil {
			log.Fatal(err)
		}

		lat := 37.7835 + float64(i)/500.0*3
		lon := -122.41 + float64(i)/500.0*4
		if hotelIdExists == 0 {
			// Insert a new row into the "geo" table
			ExecuteQuery(connection.session, `INSERT INTO geo (hotelid, lat, lon) VALUES (?, ?, ?)`, hotelID, lat, lon)
			
		}

		// Insert data into the "points" table

	}
	fmt.Println("Just when I thought I was out, they pull me back in")

	return connection.session
}
