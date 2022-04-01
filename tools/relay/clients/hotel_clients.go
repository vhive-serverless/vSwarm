package grpcclient

import (
	"fmt"
	"strings"

	geo "hotel_reserv/geo"
	profile "hotel_reserv/profile"
	rate "hotel_reserv/rate"
	recommendation "hotel_reserv/recommendation"
	reservation "hotel_reserv/reservation"
	search "hotel_reserv/search"
	user "hotel_reserv/user"

	log "github.com/sirupsen/logrus"
)

//
// Hotel reservation -----
// 1. Geo service
type HotelGeoClient struct {
	ClientBase
	client geo.GeoClient
}

func (c *HotelGeoClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = geo.NewGeoClient(c.conn)
}

func (c *HotelGeoClient) Request(req string) string {
	// Create a default forward request
	fw_req := geo.Request{
		Lat: 37.7963,
		Lon: -122.4015,
	}

	fw_res, err := c.client.Nearby(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Geo service: %v", err)
	}

	msg := fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)
	// log.Println(msg)
	return msg
}

// 2. Profile service
type HotelProfileClient struct {
	ClientBase
	client profile.ProfileClient
}

func (c *HotelProfileClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = profile.NewProfileClient(c.conn)
}

func (c *HotelProfileClient) Request(req string) string {
	_, payload := getMethodPayload(req)
	ids := strings.Split(payload, ",")
	// Create a forward request
	fw_req := profile.Request{
		HotelIds: ids,
		Locale:   "",
	}

	fw_res, err := c.client.GetProfiles(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Profile service: %v", err)
	}

	msg := fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)
	// log.Println(msg)
	return msg
}

// 3. Rate service
type HotelRateClient struct {
	ClientBase
	client rate.RateClient
}

func (c *HotelRateClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = rate.NewRateClient(c.conn)
}

func (c *HotelRateClient) Request(req string) string {
	_, payload := getMethodPayload(req)
	ids := strings.Split(payload, ",")
	// Create a forward request
	fw_req := rate.Request{
		HotelIds: ids,
		InDate:   "2015-04-09",
		OutDate:  "2015-04-11",
	}
	fw_res, err := c.client.GetRates(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Rate service: %v", err)
	}

	msg := fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)
	// log.Println(msg)
	return msg
}

// 4. Recommendation service
type HotelRecommendationClient struct {
	ClientBase
	client recommendation.RecommendationClient
}

func (c *HotelRecommendationClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = recommendation.NewRecommendationClient(c.conn)
}

func (c *HotelRecommendationClient) Request(req string) string {
	_, payload := getMethodPayload(req)
	// Create a forward request
	fw_req := recommendation.Request{
		Require: "dis",
		Lat:     37.7834,
		Lon:     -122.4081,
	}

	// If one of the require parameters is given as name we will use it
	if payload == "dis" || payload == "rate" || payload == "price" {
		fw_req.Require = req
	}

	fw_res, err := c.client.GetRecommendations(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Recommendation service: %v", err)
	}

	msg := fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)
	// log.Println(msg)
	return msg
}

// 5. Reservation service
type HotelReservationClient struct {
	ClientBase
	client reservation.ReservationClient
}

func (c *HotelReservationClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = reservation.NewReservationClient(c.conn)
}

func (c *HotelReservationClient) Request(req string) string {
	fw_method, payload := getMethodPayload(req)
	// Create a default forward request
	fw_req := reservation.Request{
		CustomerName: payload,
		HotelId:      []string{"2"},
		InDate:       "2015-04-09",
		OutDate:      "2015-04-11",
		RoomNumber:   1,
	}

	// Pass on to the real service function
	var fw_res *reservation.Result
	var err error

	switch fw_method {
	default:
	case 0:
		fw_req.HotelId[0] = "2"
		fw_res, err = c.client.CheckAvailability(c.ctx, &fw_req)
	case 1:
		fw_req.HotelId[0] = "3"
		fw_res, err = c.client.MakeReservation(c.ctx, &fw_req)
	}
	if err != nil {
		log.Fatalf("Fail to invoke Reservation service: %v", err)
	}

	msg := fmt.Sprintf("method: %d, req: %+v resp: %+v", fw_method, fw_req, *fw_res)
	// log.Println(msg)
	return msg
}

// 6. User service
type HotelUserClient struct {
	ClientBase
	client user.UserClient
}

func (c *HotelUserClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = user.NewUserClient(c.conn)
}

func (c *HotelUserClient) Request(req string) string {
	_, payload := getMethodPayload(req)
	// Create a forward request
	fw_req := user.Request{
		Username: payload,
		Password: payload,
	}

	fw_res, err := c.client.CheckUser(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke User service: %v", err)
	}

	msg := fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)
	// log.Println(msg)
	return msg
}

// 7. Search service
type HotelSearchClient struct {
	ClientBase
	client search.SearchClient
}

func (c *HotelSearchClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = search.NewSearchClient(c.conn)
}

func (c *HotelSearchClient) Request(req string) string {
	// Create a forward request
	fw_req := search.NearbyRequest{
		Lat:     37.7963,
		Lon:     -122.4015,
		InDate:  "2015-04-09",
		OutDate: "2015-04-11",
	}

	fw_res, err := c.client.Nearby(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Search service: %v", err)
	}

	msg := fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)
	// log.Println(msg)
	return msg
}
