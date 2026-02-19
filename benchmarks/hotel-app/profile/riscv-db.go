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

	// pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/profile"
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
	cqlCreateTable := `
		CREATE TABLE IF NOT EXISTS ` + tableName + `( 
			hotelid text , name text, phone_number text, 
			description text, street_number text, street_name text,
			city text, state text, country text, postal_code text,
			lat double, lon double , PRIMARY KEY (hotelid)) `
	ExecuteQuery(connection.session, cqlCreateTable)
	log.Printf("Connected OK")

	var hotelIdExists int64
	err = connection.session.Query( "SELECT COUNT(*) FROM 	"+tableName+" WHERE hotelid = ?", "1").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("Connected OK33")

	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `INSERT INTO `+tableName+`
			(hotelid, name, phone_number, description, street_number
				, street_name, city, state, country, postal_code, 
				lat, lon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
			"1", "Clift Hotel", "(415) 775-4700",
			"A 6-minute walk from Union Square and 4 minutes from a Muni Metro station, this luxury hotel designed by Philippe Starck features an artsy furniture  collection in the lobby, including work by Salvador Dali.",
			 "495", "Geary St", "San Francisco", "CA", "United States", "94102",
			 37.7867, -122.4112)
	}
	log.Printf("Connected OK4")

	err = connection.session.Query( "SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "2").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	log.Printf("Connected OK5")

	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `INSERT INTO `+tableName+`
			(hotelid, name, phone_number, description, street_number
				, street_name, city, state, country, postal_code,
				lat, lon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
			"2", "W San Francisco", "(415) 777-5300",
			"Less than a block from the Yerba Buena Center for the Arts, this trendy hotel is a 12-minute walk from Union Square.",	
					 "181", "3rd St", "San Francisco", "CA", "United States", "94103",
			 37.7854, -122.4005)
	}
	err = connection.session.Query( "SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "3").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `INSERT INTO `+tableName+`
			(hotelid, name, phone_number, description, street_number
				, street_name, city, state, country, postal_code,
				lat, lon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
			"3", "Hotel Zetta", "(415) 543-8555",
			"A 3-minute walk from the Powell Street cable-car turnaround and BART rail station, this hip hotel 9 minutes from Union Square combines high-tech lodging with artsy touches.",
			 "55", "5th St", "San Francisco", "CA", "United States", "94103",
			 37.7834, -122.4071)
	}
	err = connection.session.Query( "SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "4").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}	
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `INSERT INTO `+tableName+`
			(hotelid, name, phone_number, description, street_number
				, street_name, city, state, country, postal_code,
				lat, lon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
			"4", "Hotel Vitale", "(415) 278-3700",
			"This waterfront hotel with Bay Bridge views is 3 blocks from the Financial District and a 4-minute walk from the Ferry Building.",
			 "8", "Mission St", "San Francisco", "CA", "United States", "94105",
			 37.7936, -122.3930)
	}
	err = connection.session.Query( "SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "5").Scan(&hotelIdExists)
	if err != nil {
		log.Fatal(err)
	}	
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `INSERT INTO `+tableName+`
			(hotelid, name, phone_number, description, street_number
				, street_name, city, state, country, postal_code,
				lat, lon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
			"5", "Phoenix Hotel", "(415) 776-1380",
			"Located in the Tenderloin neighborhood, a 10-minute walk from a BART rail station, this retro motor lodge has hosted many rock musicians and other celebrities since the 1950s. It’s a 4-minute walk from the historic Great American Music Hall nightclub.",
				"601", "Eddy St","San Francisco","CA","United States",
				"94109",37.7831,-122.4181)
	}

	err = connection.session.Query( "SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", "6").Scan(&hotelIdExists)	
	if err != nil {
		log.Fatal(err)
	}	
	if hotelIdExists == 0 {
		ExecuteQuery(connection.session, `INSERT INTO `+tableName+`
			(hotelid, name, phone_number, description, street_number
				, street_name, city, state, country, postal_code,
				lat, lon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
			"6", "St. Regis San Francisco", "(415) 284-4000",
			"St. Regis Museum Tower is a 42-story, 484 ft skyscraper  in the South of Market district of San Francisco,  California, adjacent to Yerba Buena Gardens, Moscone  Center, PacBell Building and the San Francisco Museum  of Modern Art. ", "125" , "3rd St", "San Francisco", "CA",
			"United States", "94109", 37.7863, -122.4015)
	}
	// add up to 80 hotels
	for i := 7; i <= 80; i++ {
		hotel_id := strconv.Itoa(i)
		err = connection.session.Query( "SELECT COUNT(*) FROM "+tableName+" WHERE hotelid = ?", hotel_id).Scan(&hotelIdExists)
		if err != nil {
			log.Fatal(err)
		}		
		if hotelIdExists == 0 {
			phone_num := "(415) 284-40" + hotel_id
			lat := 37.7835 + float64(i)/500.0*3
			lon := -122.41 + float64(i)/500.0*4
			ExecuteQuery(connection.session, `INSERT INTO `+tableName+`
				(hotelid, name, phone_number, description, street_number
					, street_name, city, state, country, postal_code,
					lat, lon) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
					hotel_id, "St. Regis San Francisco", phone_num,
				"St. Regis Museum Tower is a 42-story, 484 ft skyscraper in the South of Market district of San Francisco, California, adjacent to Yerba Buena Gardens, Moscone Center, PacBell Building and the San Francisco Museum of Modern Art.", "125" , "3rd St", "San Francisco", "CA",
					   "United States", "94109",lat, lon)
		}
	}
	fmt.Println("Just when I thought I was out, they pull me back in")
	return connection.session
}

