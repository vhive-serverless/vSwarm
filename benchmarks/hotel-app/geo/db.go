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

	log "github.com/sirupsen/logrus"

	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

func initializeDatabase(url string) *mgo.Session {
	fmt.Printf("geo db ip addr = %s\n", url)
	session, err := mgo.Dial(url)
	if err != nil {
		panic(err)
	}
	// defer session.Close()

	c := session.DB("geo-db").C("geo")
	// First we clear the collection to have always a new one
	if err = c.DropCollection(); err != nil {
		log.Print("DropCollection: ", err)
	}

	count, err := c.Find(&bson.M{"hotelid": "1"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Point{"1", 37.7867, -122.4112})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "2"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Point{"2", 37.7854, -122.4005})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "3"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Point{"3", 37.7854, -122.4071})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "4"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Point{"4", 37.7936, -122.3930})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "5"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Point{"5", 37.7831, -122.4181})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "6"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&Point{"6", 37.7863, -122.4015})
		if err != nil {
			log.Fatal(err)
		}
	}

	// add up to 80 hotels
	for i := 7; i <= 80; i++ {
		hotel_id := strconv.Itoa(i)
		count, err = c.Find(&bson.M{"hotelid": hotel_id}).Count()
		if err != nil {
			log.Fatal(err)
		}
		lat := 37.7835 + float64(i)/500.0*3
		lon := -122.41 + float64(i)/500.0*4
		if count == 0 {
			err = c.Insert(&Point{hotel_id, lat, lon})
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
