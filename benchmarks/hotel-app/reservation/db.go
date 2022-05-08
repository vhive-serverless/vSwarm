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

	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

func initializeDatabase(url string) *mgo.Session {
	fmt.Printf("reservation db ip addr = %s\n", url)
	session, err := mgo.Dial(url)
	if err != nil {
		panic(err)
	}
	// defer session.Close()

	c := session.DB("reservation-db").C("reservation")
	// First we clear the collection to have always a new one
	if err = c.DropCollection(); err != nil {
		log.Print("DropCollection: ", err)
	}

	count, err := c.Find(&bson.M{"hotelid": "4"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Reservation{"4", "Alice", "2015-04-09", "2015-04-10", 1})
		if err != nil {
			log.Fatal(err)
		}
	}

	c = session.DB("reservation-db").C("number")
	count, err = c.Find(&bson.M{"hotelid": "1"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Number{"1", 200})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "2"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Number{"2", 10})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "3"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Number{"3", 200})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "4"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Number{"4", 200})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "5"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Number{"5", 200})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "6"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Number{"6", 200})
		if err != nil {
			log.Fatal(err)
		}
	}

	for i := 7; i <= 80; i++ {
		hotel_id := strconv.Itoa(i)
		count, err = c.Find(&bson.M{"hotelid": hotel_id}).Count()
		if err != nil {
			log.Fatal(err)
		}
		room_num := 200
		if i%3 == 1 {
			room_num = 300
		} else if i%3 == 2 {
			room_num = 250
		}
		if count == 0 {
			err = c.Insert(&Number{hotel_id, room_num})
			if err != nil {
				log.Fatal(err)
			}
		}
	}

	err = c.EnsureIndexKey("hotelid")
	if err != nil {
		log.Fatal(err)
	}

	return session
}
