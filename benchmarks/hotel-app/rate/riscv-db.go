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
		CREATE TABLE IF NOT EXISTS ` + tableName + `( 
			hotelid text, code text, indate text, outdate text,
			bookablerate double, totalrate double, totalrateinclusive double,
			roomcode text, roomdescription text,
			PRIMARY KEY (hotelid, code, indate, outdate));`
	ExecuteQuery(connection.session, cqlCreateTable)
	var hotelIdExists int64
	err = connection.session.Query(`SELECT COUNT(*) FROM `+tableName+` WHERE hotelid = ?`, "2").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `
			INSERT INTO `+tableName+`
			 (hotelid, code, indate,
				 outdate, bookablerate, totalrate,
				  totalrateinclusive, roomdescription , roomcode)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
			"1", "RACK", "2015-04-09",
			"2015-04-10", 109.00, 109.00,
			123.17, "King sized bed", "KNG")
	}
	err = connection.session.Query(`SELECT COUNT(*) FROM `+tableName+` WHERE hotelid = ?`, "2").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `
			INSERT INTO `+tableName+`
			 (hotelid, code, indate,
				 outdate, bookablerate, totalrate,
				  totalrateinclusive, roomdescription, roomcode)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
			"2", "RACK", "2015-04-09",
			"2015-04-10", 139.00, 139.00,
			153.09, "Queen sized bed", "QN")
	}
	err = connection.session.Query(`SELECT COUNT(*) FROM `+tableName+` WHERE hotelid = ?`, "3").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `
			INSERT INTO `+tableName+`
			 (hotelid, code, indate,
				 outdate, bookablerate, totalrate,
				  totalrateinclusive, roomdescription, roomcode)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
			"3", "RACK", "2015-04-09",
			"2015-04-10", 109.00, 109.00,
			123.17, "King sized bed", "KNG")
	}
	// add up to 80 hotels
	for i := 7; i <= 80; i++ {
		if i%3 == 0 {
			hotel_id := strconv.Itoa(i)
			err = connection.session.Query(`SELECT COUNT(*) FROM `+tableName+` WHERE hotelid = ?`, hotel_id).Scan(&hotelIdExists)
			if err != nil {
				log.Fatal(err)
			}
			end_date := "2015-04-"
			rate := 109.00
			rate_inc := 123.17
			if i%2 == 0 {
				end_date = end_date + "17"
			} else {
				end_date = end_date + "24"
			}

			if i%5 == 1 {
				rate = 120.00
				rate_inc = 140.00
			} else if i%5 == 2 {
				rate = 124.00
				rate_inc = 144.00
			} else if i%5 == 3 {
				rate = 132.00
				rate_inc = 158.00
			} else if i%5 == 4 {
				rate = 232.00
				rate_inc = 258.00
			}
			if hotelIdExists == 0 {
				ExecuteQuery(connection.session, `
					INSERT INTO `+tableName+`
					 (hotelid, code, indate,
						 outdate, bookablerate, totalrate,
						  totalrateinclusive, roomdescription, roomcode)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
					hotel_id, "RACK", "2015-04-09",
					end_date, rate, rate,
					rate_inc, "King sized bed", "KNG")
			}
		}
	}
	fmt.Println("Just when I thought I was out, they pull me back in")
	return connection.session
}
