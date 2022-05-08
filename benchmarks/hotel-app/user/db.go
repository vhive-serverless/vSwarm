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
	"crypto/sha256"
	"fmt"
	"log"

	"strconv"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func connectDatabase(ctx context.Context, url string) *mongo.Client {
	fmt.Printf("user db ip addr = %s\n", url)
	// ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	// defer cancel()
	url_s := fmt.Sprintf("mongodb://%s", url)
	session, err := mongo.Connect(ctx, options.Client().ApplyURI(url_s))
	if err != nil {
		panic(err)
	}
	return session
}

func initializeDatabase(ctx context.Context, c *mongo.Client) {

	// Read the initial users
	users := make([]User, 500)
	users[0].Username = "hello"
	users[0].Password = "hello"

	// readJson(&users, *initdata)
	// fmt.Println(users)

	// Create users
	for i := 1; i < len(users); i++ {
		suffix := strconv.Itoa(i)
		users[i].Username = "user_" + suffix
		users[i].Password = "pass_" + suffix
	}

	// Insert in Database
	coll := c.Database("user-db").Collection("user")
	// Clear any existing data

	if err := coll.Drop(ctx); err != nil {
		log.Print("DropCollection: ", err)
	}

	// u := User{"Hello", "test"}
	// res, err := coll.InsertOne(ctx, u)

	// sum := sha256.Sum256([]byte(u.Password))
	// pass := fmt.Sprintf("%x", sum)

	// fmt.Println("Insert User in DB: ", u.Username, " ", u.Password, " ", pass)

	// create the database records
	elements := make([]interface{}, len(users))
	for i := range users {
		sum := sha256.Sum256([]byte(users[i].Password))
		pass := fmt.Sprintf("%x", sum)
		elements[i] = bson.M{"username": users[i].Username, "password": pass}
	}

	// Insert them into the data base
	opts := options.InsertMany().SetOrdered(false)
	_, err := coll.InsertMany(ctx, elements, opts)
	if err != nil {
		log.Fatal(err)
	}
	// fmt.Printf("inserted documents with IDs %v\n", res.InsertedIDs)

	// listCollection(ctx, coll)
}

// func listCollection(ctx context.Context, coll *mongo.Collection) {

// 	// Find all documents in which the "username" field is "Bob".
// 	// Find all documents.
// 	cursor, err := coll.Find(ctx, bson.D{})
// 	if err != nil {
// 		log.Fatal(err)
// 	}

// 	// Get a list of all returned documents and print them out.
// 	// See the mongo.Cursor documentation for more examples of using cursors.
// 	var results []bson.M
// 	if err = cursor.All(ctx, &results); err != nil {
// 		log.Fatal(err)
// 	}
// 	for _, result := range results {
// 		fmt.Println(result)
// 	}
// }

// func readJson(data interface{}, filename string) {
// 	content, err := ioutil.ReadFile(filename)
// 	if err != nil {
// 		log.Fatalln(err)
// 	}

// 	err = json.Unmarshal(content, data)
// 	if err != nil {
// 		log.Fatalln("error:", err)
// 	}
// }
