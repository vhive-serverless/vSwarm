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
	// "context"
	"crypto/sha256"
	"fmt"
	"log"
	"time"
	"strconv"
	"github.com/gocql/gocql"

	// "go.mongodb.org/mongo-driver/bson"
	// "go.mongodb.org/mongo-driver/mongo"
	// "go.mongodb.org/mongo-driver/mongo/options"
)
type DBConnection struct {
	cluster *gocql.ClusterConfig
	session *gocql.Session
}
func connectCassandra( url string, action string) *gocql.Session {
    // Print Cassandra contact points
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

    // Create the session with con    session, err := cluster.CreateSession(ctx)

	for {
		connection.session, err = connection.cluster.CreateSession()
		if err == nil {
			break
		}
		log.Printf("CreateSession: %v", err)
		time.Sleep(15*time.Second)
	}
	fmt.Println("Keyspace " + keyspaceName + " created successfully.")
	tableName := action
	cqlDropTable := `DROP TABLE IF EXISTS ` + tableName
	if err = connection.session.Query(cqlDropTable).Exec(); err != nil {
		log.Fatal(err)
	}
	cqlCreateTable := `
		CREATE TABLE IF NOT EXISTS ` + tableName + `( 
			username text , password text , PRIMARY KEY (username)) `
	if err = connection.session.Query(cqlCreateTable).Exec(); err != nil {
		log.Fatal(err)
	}
    return connection.session
}



func initializeDatabase(session *gocql.Session, keyspace string, tableName string) {


	// Read the initial users

	users := make([]User, 500)
	users[0].Username = "hello"
	users[0].Password = "hello"

	// Create users
	for i := 1; i < len(users); i++ {
		suffix := strconv.Itoa(i)
		users[i].Username = "user_" + suffix
		users[i].Password = "pass_" + suffix
	}
	const batchSize = 100 // Adjust based on your needs and testing
	fmt.Printf(tableName)
	for i := 0; i < len(users); i += batchSize {
		end := i + batchSize
		if end > len(users) {
			end = len(users)
		}
	
		batch := gocql.NewBatch(gocql.LoggedBatch)
		for _, user := range users[i:end] {
			sum := sha256.Sum256([]byte(user.Password))
			pass := fmt.Sprintf("%x", sum)
			batch.Query("INSERT INTO "+tableName+" (username, password) VALUES (?,?)", user.Username, pass)
		}
	
		// Execute the batch
		if err := session.ExecuteBatch(batch); err!= nil {
			log.Fatalf("Failed to insert users: %v", err)
		}
	}
	

	
}





