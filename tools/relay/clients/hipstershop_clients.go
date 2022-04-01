package grpcclient

import (
	"fmt"
	"strconv"

	pb "hipstershop/proto"
	log "github.com/sirupsen/logrus"
)

var (
	defEmail      = "jonny.depp@gmail.com"
	defCurrency   = "USD"
	defCreditCard = pb.CreditCardInfo{
		CreditCardNumber:          "5496524458927653",
		CreditCardCvv:             123,
		CreditCardExpirationYear:  2025,
		CreditCardExpirationMonth: 3,
	}
	defAddress = pb.Address{
		StreetAddress: "7846 Coffee St.",
		City:          "Pittsford",
		State:         "NY",
		Country:       "US",
		ZipCode:       14534,
	}
	defCartItem1 = pb.CartItem{
		ProductId: "OLJCESPC7Z",
		Quantity:  3,
	}
	defCartItem2 = pb.CartItem{
		ProductId: "LS4PSXUNUM",
		Quantity:  2,
	}
	defMoney = pb.Money{
		CurrencyCode: "USD",
		Units:        100,
		Nanos:        10,
	}

	item1 = pb.OrderItem{
		Item: &pb.CartItem{ProductId: "1111", Quantity: 1},
		Cost: &pb.Money{CurrencyCode: "USD", Units: 111, Nanos: 11},
	}
	item2 = pb.OrderItem{
		Item: &pb.CartItem{ProductId: "2222", Quantity: 2},
		Cost: &pb.Money{CurrencyCode: "USD", Units: 222, Nanos: 22},
	}
	item3 = pb.OrderItem{
		Item: &pb.CartItem{ProductId: "333", Quantity: 3},
		Cost: &pb.Money{CurrencyCode: "USD", Units: 333, Nanos: 33},
	}

	defOrder = pb.OrderResult{
		OrderId:            "123",
		ShippingTrackingId: "345",
		ShippingCost:       &defMoney,
		ShippingAddress:    &defAddress,
		Items:              []*pb.OrderItem{&item1, &item2, &item3},
	}
	product1 = pb.Product{
		Id:          "OLJCESPC7Z",
		Name:        "Coffee",
		Description: "Beans with a smooth and flowery chocolate finish.",
		Picture:     "/static/img/products/coffee-beans.jpg",
		PriceUsd:    &pb.Money{CurrencyCode: "USD", Units: 18, Nanos: 990000000},
		Categories:  []string{"coffee"},
	}
	defProductId1 = "OLJCESPC7Z"
	defProductId2 = "LS4PSXUNUM"
)

//
// ------- Ad Service --------
type ShopAdServiceClient struct {
	ClientBase
	client pb.AdServiceClient
}

func (c *ShopAdServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewAdServiceClient(c.conn)
}

func (c *ShopAdServiceClient) Request(req string) string {

	_, payload := getMethodPayload(req)
	// Create a default forward request
	fw_req := pb.AdRequest{
		ContextKeys: []string{payload},
	}

	fw_res, err := c.client.GetAds(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Ad service: %v", err)
	}

	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg
}

//
// ------- Cart Service --------
//
type ShopCartServiceClient struct {
	ClientBase
	client pb.CartServiceClient
}

func (c *ShopCartServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewCartServiceClient(c.conn)
}

func (c *ShopCartServiceClient) Request(req string) string {

	fw_method, payload := getMethodPayload(req)

	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	default:
	case 0: // Method 1: AddItem
		fw_req := pb.AddItemRequest{
			UserId: payload,
			Item:   &defCartItem1,
		}
		var fw_res *pb.Empty
		fw_res, err = c.client.AddItem(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	case 1: // Method 2: GetCart
		fw_req := pb.GetCartRequest{
			UserId: payload,
		}
		var fw_res *pb.Cart
		fw_res, err = c.client.GetCart(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	case 2: // Method 3: EmptyCart
		fw_req := pb.EmptyCartRequest{
			UserId: payload,
		}
		var fw_res *pb.Empty
		fw_res, err = c.client.EmptyCart(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	}
	if err != nil {
		log.Fatalf("Fail to invoke Cart service: %v", err)
	}

	msg = fmt.Sprintf("method: %d, %s", fw_method, msg)
	// log.Println(msg)
	return msg
}

//
// ------- Checkout Service --------
//
type ShopCheckoutServiceClient struct {
	ClientBase
	client pb.CheckoutServiceClient
}

func (c *ShopCheckoutServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewCheckoutServiceClient(c.conn)
}

func (c *ShopCheckoutServiceClient) Request(req string) string {

	// Pass on to the real service function
	_, payload := getMethodPayload(req)

	// Create a forward request
	fw_req := pb.PlaceOrderRequest{
		UserId:       payload,
		UserCurrency: defCurrency,
		Address:      &defAddress,
		Email:        defEmail,
		CreditCard:   &defCreditCard,
	}

	fw_res, err := c.client.PlaceOrder(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Checkout service: %v", err)
	}

	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg
}

//
// ------- Currency Service --------
//
type ShopCurrencyServiceClient struct {
	ClientBase
	client pb.CurrencyServiceClient
}

func (c *ShopCurrencyServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewCurrencyServiceClient(c.conn)
}

func (c *ShopCurrencyServiceClient) Request(req string) string {

	fw_method, payload := getMethodPayload(req)
	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	default:
	case 0: // Method 1: GetSupportedCurrencies
		fw_req := pb.Empty{}
		var fw_res *pb.GetSupportedCurrenciesResponse
		fw_res, err = c.client.GetSupportedCurrencies(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	case 1: // Method 2: Convert
		fw_req := pb.CurrencyConversionRequest{
			From:   &defMoney,
			ToCode: "EUR",
		}
		if v, err := strconv.ParseInt(payload, 10, 64); err == nil {
			fw_req.From.Units = v
		}

		var fw_res *pb.Money
		fw_res, err = c.client.Convert(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)
	}
	if err != nil {
		log.Fatalf("Fail to invoke Currency service: %v", err)
	}

	msg = fmt.Sprintf("method: %d, %s", fw_method, msg)
	// log.Println(msg)
	return msg
}

//
// ------- Email Service --------
//
type ShopEmailServiceClient struct {
	ClientBase
	client pb.EmailServiceClient
}

func (c *ShopEmailServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewEmailServiceClient(c.conn)
}

func (c *ShopEmailServiceClient) Request(req string) string {

	// Pass on to the real service function
	// _, payload := getMethodPayload(req)

	// Create a forward request
	fw_req := pb.SendOrderConfirmationRequest{
		Email: defEmail,
		Order: &defOrder,
	}

	fw_res, err := c.client.SendOrderConfirmation(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Email service: %v", err)
	}

	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg

}

//
// ------- Payment Service --------
//
type ShopPaymentServiceClient struct {
	ClientBase
	client pb.PaymentServiceClient
}

func (c *ShopPaymentServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewPaymentServiceClient(c.conn)
}

func (c *ShopPaymentServiceClient) Request(req string) string {

	_, payload := getMethodPayload(req)
	// Create a default forward request
	fw_req := pb.ChargeRequest{
		Amount:     &defMoney,
		CreditCard: &defCreditCard,
	}

	if v, err := strconv.ParseInt(payload, 10, 64); err == nil {
		fw_req.Amount.Units = v
	}

	fw_res, err := c.client.Charge(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Payment service: %v", err)
	}

	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg
}

//
// ------- ProductCatalog Service --------
//
type ShopProductCatalogServiceClient struct {
	ClientBase
	client pb.ProductCatalogServiceClient
}

func (c *ShopProductCatalogServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewProductCatalogServiceClient(c.conn)
}

func (c *ShopProductCatalogServiceClient) Request(req string) string {

	fw_method, payload := getMethodPayload(req)

	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	default:
	case 0: // Method 1: ListProducts
		fw_req := pb.Empty{}
		var fw_res *pb.ListProductsResponse
		fw_res, err = c.client.ListProducts(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	case 1: // Method 2: GetProduct
		fw_req := pb.GetProductRequest{
			Id: payload,
		}
		var fw_res *pb.Product
		fw_res, err = c.client.GetProduct(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	case 2: // Method 3: SearchProducts
		fw_req := pb.SearchProductsRequest{
			Query: payload,
		}
		var fw_res *pb.SearchProductsResponse
		fw_res, err = c.client.SearchProducts(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	}
	if err != nil {
		log.Fatalf("Fail to invoke ProductCatalog service: %v", err)
	}

	msg = fmt.Sprintf("method: %d, %s", fw_method, msg)
	// log.Println(msg)
	return msg
}

//
// ------- Recommendation Service --------
//
type ShopRecommendationServiceClient struct {
	ClientBase
	client pb.RecommendationServiceClient
}

func (c *ShopRecommendationServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewRecommendationServiceClient(c.conn)
}

func (c *ShopRecommendationServiceClient) Request(req string) string {

	_, payload := getMethodPayload(req)
	// Create a default forward request
	fw_req := pb.ListRecommendationsRequest{
		UserId:     payload,
		ProductIds: []string{defProductId1, defProductId2},
	}

	fw_res, err := c.client.ListRecommendations(c.ctx, &fw_req)
	if err != nil {
		log.Fatalf("Fail to invoke Recommendation service: %v", err)
	}
	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg
}

//
// ------- Shipping Service --------
//
type ShopShippingServiceClient struct {
	ClientBase
	client pb.ShippingServiceClient
}

func (c *ShopShippingServiceClient) Init(ip, port string) {
	c.Connect(ip, port)
	c.client = pb.NewShippingServiceClient(c.conn)
}

func (c *ShopShippingServiceClient) Request(req string) string {

	fw_method, _ := getMethodPayload(req)

	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	default:
	case 0: // Method 1: GetQuote
		fw_req := pb.GetQuoteRequest{
			Address: &defAddress,
			Items:   []*pb.CartItem{&defCartItem1, &defCartItem2},
		}
		var fw_res *pb.GetQuoteResponse
		fw_res, err = c.client.GetQuote(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	case 1: // Method 2: ShipOrder
		fw_req := pb.ShipOrderRequest{
			Address: &defAddress,
			Items:   []*pb.CartItem{&defCartItem1, &defCartItem2},
		}
		var fw_res *pb.ShipOrderResponse
		fw_res, err = c.client.ShipOrder(c.ctx, &fw_req)
		msg = fmt.Sprintf("req: %+v resp: %+v", fw_req, fw_res)

	}
	if err != nil {
		log.Fatalf("Fail to invoke Shipping service: %v", err)
	}

	msg = fmt.Sprintf("method: %d, %s", fw_method, msg)
	// log.Println(msg)
	return msg
}
