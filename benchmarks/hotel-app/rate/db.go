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

	pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/rate"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

func initializeDatabase(url string) *mgo.Session {
	fmt.Printf("rate db ip addr = %s\n", url)
	session, err := mgo.Dial(url)
	if err != nil {
		panic(err)
	}
	// defer session.Close()

	c := session.DB("rate-db").C("inventory")
	// First we clear the collection to have always a new one
	if err = c.DropCollection(); err != nil {
		log.Print("DropCollection: ", err)
	}
	count, err := c.Count()
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf(" Collection contains: %d elements\n", count)
	count, err = c.Find(&bson.M{"hotelid": "2"}).Count()
	if err != nil {
		log.Fatal(err)
	}

	item := pb.RatePlan{
		HotelId: "1",
		Code:    "RACK",
		InDate:  "2015-04-09",
		OutDate: "2015-04-10",
		RoomType: &pb.RoomType{
			BookableRate:       109.00,
			Code:               "KNG",
			RoomDescription:    "King sized bed",
			TotalRate:          109.00,
			TotalRateInclusive: 123.17,
		},
	}

	if count == 0 {
		err = c.Insert(&item)
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "2"}).Count()
	if err != nil {
		log.Fatal(err)
	}

	item.HotelId = "2"
	item.Code = "RACK"
	item.InDate = "2015-04-09"
	item.OutDate = "2015-04-10"
	item.RoomType.BookableRate = 139.00
	item.RoomType.Code = "QN"
	item.RoomType.RoomDescription = "Queen sized bed"
	item.RoomType.TotalRate = 139.00
	item.RoomType.TotalRateInclusive = 153.09

	if count == 0 {
		err = c.Insert(&item)
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"hotelid": "3"}).Count()
	if err != nil {
		log.Fatal(err)
	}

	item.HotelId = "3"
	item.Code = "RACK"
	item.InDate = "2015-04-09"
	item.OutDate = "2015-04-10"
	item.RoomType.BookableRate = 109.00
	item.RoomType.Code = "KNG"
	item.RoomType.RoomDescription = "King sized bed"
	item.RoomType.TotalRate = 109.00
	item.RoomType.TotalRateInclusive = 123.17

	if count == 0 {
		err = c.Insert(&item)
		if err != nil {
			log.Fatal(err)
		}
	}

	// add up to 80 hotels
	for i := 7; i <= 80; i++ {
		if i%3 == 0 {
			hotel_id := strconv.Itoa(i)
			count, err = c.Find(&bson.M{"hotelid": hotel_id}).Count()
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

			if count == 0 {

				item.HotelId = hotel_id
				item.Code = "RACK"
				item.InDate = "2015-04-09"
				item.OutDate = end_date
				item.RoomType.BookableRate = rate
				item.RoomType.Code = "KNG"
				item.RoomType.RoomDescription = "King sized bed"
				item.RoomType.TotalRate = rate
				item.RoomType.TotalRateInclusive = rate_inc

				err = c.Insert(&item)
				if err != nil {
					log.Fatal(err)
				}
			}
		}
	}

	err = c.EnsureIndexKey("hotelid")
	if err != nil {
		log.Fatal(err)
	}

	return session
}
