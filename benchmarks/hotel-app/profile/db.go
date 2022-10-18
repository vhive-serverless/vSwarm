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

	pb "github.com/vhive-serverless/vSwarm-proto/proto/hotel_reserv/profile"
	"gopkg.in/mgo.v2"
	"gopkg.in/mgo.v2/bson"
)

func initializeDatabase(url string) *mgo.Session {
	fmt.Printf("profile db ip addr = %s\n", url)
	session, err := mgo.Dial(url)
	if err != nil {
		panic(err)
	}
	// defer session.Close()

	c := session.DB("profile-db").C("hotels")
	// First we clear the collection to have always a new one
	if err = c.DropCollection(); err != nil {
		log.Print("DropCollection: ", err)
	}

	count, err := c.Find(&bson.M{"id": "1"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&pb.Hotel{
			Id:          "1",
			Name:        "Clift Hotel",
			PhoneNumber: "(415) 775-4700",
			Description: "A 6-minute walk from Union Square and 4 minutes from a Muni Metro station, this luxury hotel designed by Philippe Starck features an artsy furniture collection in the lobby, including work by Salvador Dali.",
			Address: &pb.Address{
				StreetNumber: "495",
				StreetName:   "Geary St",
				City:         "San Francisco",
				State:        "CA",
				Country:      "United States",
				PostalCode:   "94102",
				Lat:          37.7867,
				Lon:          -122.4112}})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"id": "2"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&pb.Hotel{
			Id:          "2",
			Name:        "W San Francisco",
			PhoneNumber: "(415) 777-5300",
			Description: "Less than a block from the Yerba Buena Center for the Arts, this trendy hotel is a 12-minute walk from Union Square.",
			Address: &pb.Address{
				StreetNumber: "181",
				StreetName:   "3rd St",
				City:         "San Francisco",
				State:        "CA",
				Country:      "United States",
				PostalCode:   "94103",
				Lat:          37.7854,
				Lon:          -122.4005}})
		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"id": "3"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&pb.Hotel{
			Id:          "3",
			Name:        "Hotel Zetta",
			PhoneNumber: "(415) 543-8555",
			Description: "A 3-minute walk from the Powell Street cable-car turnaround and BART rail station, this hip hotel 9 minutes from Union Square combines high-tech lodging with artsy touches.",
			Address: &pb.Address{
				StreetNumber: "55",
				StreetName:   "5th St",
				City:         "San Francisco",
				State:        "CA",
				Country:      "United States",
				PostalCode:   "94103",
				Lat:          37.7834,
				Lon:          -122.4071}})

		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"id": "4"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&pb.Hotel{
			Id:          "4",
			Name:        "Hotel Vitale",
			PhoneNumber: "(415) 278-3700",
			Description: "This waterfront hotel with Bay Bridge views is 3 blocks from the Financial District and a 4-minute walk from the Ferry Building.",
			Address: &pb.Address{
				StreetNumber: "8",
				StreetName:   "Mission St",
				City:         "San Francisco",
				State:        "CA",
				Country:      "United States",
				PostalCode:   "94105",
				Lat:          37.7936,
				Lon:          -122.3930}})

		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"id": "5"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&pb.Hotel{
			Id:          "5",
			Name:        "Phoenix Hotel",
			PhoneNumber: "(415) 776-1380",
			Description: "Located in the Tenderloin neighborhood, a 10-minute walk from a BART rail station, this retro motor lodge has hosted many rock musicians and other celebrities since the 1950s. It’s a 4-minute walk from the historic Great American Music Hall nightclub.",
			Address: &pb.Address{
				StreetNumber: "601",
				StreetName:   "Eddy St",
				City:         "San Francisco",
				State:        "CA",
				Country:      "United States",
				PostalCode:   "94109",
				Lat:          37.7831,
				Lon:          -122.4181}})

		if err != nil {
			log.Fatal(err)
		}
	}

	count, err = c.Find(&bson.M{"id": "6"}).Count()
	if err != nil {
		log.Fatal(err)
	}
	if count == 0 {
		err = c.Insert(&pb.Hotel{
			Id:          "6",
			Name:        "St. Regis San Francisco",
			PhoneNumber: "(415) 284-4000",
			Description: "St. Regis Museum Tower is a 42-story, 484 ft skyscraper in the South of Market district of San Francisco, California, adjacent to Yerba Buena Gardens, Moscone Center, PacBell Building and the San Francisco Museum of Modern Art.",
			Address: &pb.Address{
				StreetNumber: "125",
				StreetName:   "3rd St",
				City:         "San Francisco",
				State:        "CA",
				Country:      "United States",
				PostalCode:   "94109",
				Lat:          37.7863,
				Lon:          -122.4015}})

		if err != nil {
			log.Fatal(err)
		}
	}

	// add up to 80 hotels
	for i := 7; i <= 80; i++ {
		hotel_id := strconv.Itoa(i)
		count, err = c.Find(&bson.M{"id": hotel_id}).Count()
		if err != nil {
			log.Fatal(err)
		}
		phone_num := "(415) 284-40" + hotel_id
		lat := 37.7835 + float32(i)/500.0*3
		lon := -122.41 + float32(i)/500.0*4
		if count == 0 {
			err = c.Insert(&pb.Hotel{
				Id:          hotel_id,
				Name:        "St. Regis San Francisco",
				PhoneNumber: phone_num,
				Description: "St. Regis Museum Tower is a 42-story, 484 ft skyscraper in the South of Market district of San Francisco, California, adjacent to Yerba Buena Gardens, Moscone Center, PacBell Building and the San Francisco Museum of Modern Art.",
				Address: &pb.Address{
					StreetNumber: "125",
					StreetName:   "3rd St",
					City:         "San Francisco",
					State:        "CA",
					Country:      "United States",
					PostalCode:   "94109",
					Lat:          lat,
					Lon:          lon}})

			if err != nil {
				log.Fatal(err)
			}
		}
	}

	err = c.EnsureIndexKey("id")
	if err != nil {
		log.Fatal(err)
	}

	return session
}
