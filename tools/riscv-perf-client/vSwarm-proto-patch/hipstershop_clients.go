package grpcclient

import (
	"context"
	"fmt"
	"strconv"

	log "github.com/sirupsen/logrus"
	pb "github.com/vhive-serverless/vSwarm-proto/proto/hipstershop"
)

var (
	defEmail      = "jonny.depp@gmail.com"
	defCurrency   = "USD"
	defCreditCard = pb.CreditCardInfo{
		CreditCardNumber:          "5496524458927653",
		CreditCardCvv:             123,
		CreditCardExpirationYear:  2029,
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
	defProductId1 = "OLJCESPC7Z"
	defProductId2 = "LS4PSXUNUM"
)

// ------- Ad Service --------
type ShopAdServiceClient struct {
	ClientBase
	client pb.AdServiceClient
}

func (c *ShopAdServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewAdServiceClient(c.conn)
	return nil
}

func (c *ShopAdServiceClient) Request(ctx context.Context, req Input) (string, error) {

	payload := req.Value
	// Create a default forward request
	fw_req := pb.AdRequest{
		ContextKeys: []string{payload},
	}

	fw_res, err := c.client.GetAds(ctx, &fw_req)
	if err != nil {
		return "", err
	}

	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg, nil
}

type ShopAdServiceGenerator struct {
	GeneratorBase
}

func (g *ShopAdServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopAdServiceClient) GetGenerator() Generator {
	return new(ShopAdServiceGenerator)
}

// ------- Cart Service --------
type ShopCartServiceClient struct {
	ClientBase
	client pb.CartServiceClient
}

func (c *ShopCartServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewCartServiceClient(c.conn)
	return nil
}

func (c *ShopCartServiceClient) Request(ctx context.Context, req Input) (string, error) {

	fw_method := req.Method
	payload := req.Value
	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	case "AddItem", "0": // Method 1: AddItem
		fw_req := pb.AddItemRequest{
			UserId: payload,
			Item:   &defCartItem1,
		}
		var fw_res *pb.Empty
		fw_res, err = c.client.AddItem(ctx, &fw_req)
		msg = fmt.Sprintf("req: {UserId: %s, Item: %+v} resp: %+v", payload, &defCartItem1, fw_res)

	case "GetCart", "1": // Method 2: GetCart
		fw_req := pb.GetCartRequest{
			UserId: payload,
		}
		var fw_res *pb.Cart
		fw_res, err = c.client.GetCart(ctx, &fw_req)
		msg = fmt.Sprintf("req: {UserId: %s} resp: %+v", payload, fw_res)

	case "EmptyCart", "2": // Method 3: EmptyCart
		fw_req := pb.EmptyCartRequest{
			UserId: payload,
		}
		var fw_res *pb.Empty
		fw_res, err = c.client.EmptyCart(ctx, &fw_req)
		msg = fmt.Sprintf("req: {UserId: %s} resp: %+v", payload, fw_res)

	default:
		log.Fatalf("Failed to understand requested method: %s", fw_method)

	}
	if err != nil {
		return "", err
	}

	msg = fmt.Sprintf("method: %s, %s", fw_method, msg)
	// log.Println(msg)
	return msg, nil
}

type ShopCartServiceGenerator struct {
	GeneratorBase
}

func (g *ShopCartServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopCartServiceClient) GetGenerator() Generator {
	return new(ShopCartServiceGenerator)
}

// ------- Checkout Service --------
type ShopCheckoutServiceClient struct {
	ClientBase
	client pb.CheckoutServiceClient
}

func (c *ShopCheckoutServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewCheckoutServiceClient(c.conn)
	return nil
}

func (c *ShopCheckoutServiceClient) Request(ctx context.Context, req Input) (string, error) {

	// Pass on to the real service function
	payload := req.Value

	// Create a forward request
	fw_req := pb.PlaceOrderRequest{
		UserId:       payload,
		UserCurrency: defCurrency,
		Address:      &defAddress,
		Email:        defEmail,
		CreditCard:   &defCreditCard,
	}

	fw_res, err := c.client.PlaceOrder(ctx, &fw_req)
	if err != nil {
		return "", err
	}

	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg, nil
}

type ShopCheckoutServiceGenerator struct {
	GeneratorBase
}

func (g *ShopCheckoutServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopCheckoutServiceClient) GetGenerator() Generator {
	return new(ShopCheckoutServiceGenerator)
}

// ------- Currency Service --------
type ShopCurrencyServiceClient struct {
	ClientBase
	client pb.CurrencyServiceClient
}

func (c *ShopCurrencyServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewCurrencyServiceClient(c.conn)
	return nil
}

func (c *ShopCurrencyServiceClient) Request(ctx context.Context, req Input) (string, error) {

	fw_method, payload := req.Method, req.Value
	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	case "GetSupportedCurrencies", "0": // Method 1: GetSupportedCurrencies
		fw_req := pb.Empty{}
		var fw_res *pb.GetSupportedCurrenciesResponse
		fw_res, err = c.client.GetSupportedCurrencies(ctx, &fw_req)
		msg = fmt.Sprintf("req: {} resp: %+v", fw_res)

	case "Convert", "1": // Method 2: Convert
		fw_req := pb.CurrencyConversionRequest{
			From:   &defMoney,
			ToCode: "EUR",
		}
		if v, err := strconv.ParseInt(payload, 10, 64); err == nil {
			fw_req.From.Units = v
		}

		var fw_res *pb.Money
		fw_res, err = c.client.Convert(ctx, &fw_req)
		msg = fmt.Sprintf("req: {From: %+v, ToCode: \"EUR\"} resp: %+v", &defMoney, fw_res)

	default:
		log.Fatalf("Failed to understand requested method: %s", fw_method)
	}
	if err != nil {
		return "", err
	}

	msg = fmt.Sprintf("method: %s, %s", fw_method, msg)
	// log.Println(msg)
	return msg, nil
}

type ShopCurrencyServiceGenerator struct {
	GeneratorBase
}

func (g *ShopCurrencyServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopCurrencyServiceClient) GetGenerator() Generator {
	return new(ShopCurrencyServiceGenerator)
}

// ------- Email Service --------
type ShopEmailServiceClient struct {
	ClientBase
	client pb.EmailServiceClient
}

func (c *ShopEmailServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewEmailServiceClient(c.conn)
	return nil
}

func (c *ShopEmailServiceClient) Request(ctx context.Context, req Input) (string, error) {

	// Pass on to the real service function
	// _, payload := getMethodPayload(req)

	// Create a forward request
	fw_req := pb.SendOrderConfirmationRequest{
		Email: defEmail,
		Order: &defOrder,
	}

	fw_res, err := c.client.SendOrderConfirmation(ctx, &fw_req)
	if err != nil {
		return "", err
	}
	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg, nil

}

type ShopEmailServiceGenerator struct {
	GeneratorBase
}

func (g *ShopEmailServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopEmailServiceClient) GetGenerator() Generator {
	return new(ShopEmailServiceGenerator)
}

// ------- Payment Service --------
type ShopPaymentServiceClient struct {
	ClientBase
	client pb.PaymentServiceClient
}

func (c *ShopPaymentServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewPaymentServiceClient(c.conn)
	return nil
}

func (c *ShopPaymentServiceClient) Request(ctx context.Context, req Input) (string, error) {

	payload := req.Value
	// Create a default forward request
	fw_req := pb.ChargeRequest{
		Amount:     &defMoney,
		CreditCard: &defCreditCard,
	}

	if v, err := strconv.ParseInt(payload, 10, 64); err == nil {
		fw_req.Amount.Units = v
	}

	fw_res, err := c.client.Charge(ctx, &fw_req)
	if err != nil {
		return "", err
	}

	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg, nil
}

type ShopPaymentServiceGenerator struct {
	GeneratorBase
}

func (g *ShopPaymentServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopPaymentServiceClient) GetGenerator() Generator {
	return new(ShopPaymentServiceGenerator)
}

// ------- ProductCatalog Service --------
type ShopProductCatalogServiceClient struct {
	ClientBase
	client pb.ProductCatalogServiceClient
}

func (c *ShopProductCatalogServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewProductCatalogServiceClient(c.conn)
	return nil
}

func (c *ShopProductCatalogServiceClient) Request(ctx context.Context, req Input) (string, error) {

	fw_method := req.Method
	payload := req.Value

	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	case "ListProducts", "0": // Method 1: ListProducts
		fw_req := pb.Empty{}
		var fw_res *pb.ListProductsResponse
		fw_res, err = c.client.ListProducts(ctx, &fw_req)
		msg = fmt.Sprintf("req: {} resp: %+v", fw_res)

	case "GetProduct", "1": // Method 2: GetProduct
		fw_req := pb.GetProductRequest{
			Id: payload,
		}
		var fw_res *pb.Product
		fw_res, err = c.client.GetProduct(ctx, &fw_req)
		msg = fmt.Sprintf("req: {Id: %s} resp: %+v", payload, fw_res)

	case "SearchProducts", "2": // Method 3: SearchProducts
		fw_req := pb.SearchProductsRequest{
			Query: payload,
		}
		var fw_res *pb.SearchProductsResponse
		fw_res, err = c.client.SearchProducts(ctx, &fw_req)
		msg = fmt.Sprintf("req: {Query: %s} resp: %+v", payload, fw_res)

	default:
		log.Fatalf("Failed to understand requested method: %s", fw_method)
	}
	if err != nil {
		return "", err
	}

	msg = fmt.Sprintf("method: %s, %s", fw_method, msg)
	// log.Println(msg)
	return msg, nil
}

type ShopProductCatalogServiceGenerator struct {
	GeneratorBase
}

func (g *ShopProductCatalogServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopProductCatalogServiceClient) GetGenerator() Generator {
	return new(ShopProductCatalogServiceGenerator)
}

// ------- Recommendation Service --------
type ShopRecommendationServiceClient struct {
	ClientBase
	client pb.RecommendationServiceClient
}

func (c *ShopRecommendationServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewRecommendationServiceClient(c.conn)
	return nil
}

func (c *ShopRecommendationServiceClient) Request(ctx context.Context, req Input) (string, error) {

	payload := req.Value
	// Create a default forward request
	fw_req := pb.ListRecommendationsRequest{
		UserId:     payload,
		ProductIds: []string{defProductId1, defProductId2},
	}

	fw_res, err := c.client.ListRecommendations(ctx, &fw_req)
	if err != nil {
		return "", err
	}
	msg := fmt.Sprintf("%+v", fw_res)
	// log.Println(msg)
	return msg, nil
}

type ShopRecommendationServiceGenerator struct {
	GeneratorBase
}

func (g *ShopRecommendationServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopRecommendationServiceClient) GetGenerator() Generator {
	return new(ShopRecommendationServiceGenerator)
}

// ------- Shipping Service --------
type ShopShippingServiceClient struct {
	ClientBase
	client pb.ShippingServiceClient
}

func (c *ShopShippingServiceClient) Init(ctx context.Context, ip, port string) error {
	err := c.Connect(ctx, ip, port)
	if err != nil {
		return err
	}
	c.client = pb.NewShippingServiceClient(c.conn)
	return nil
}

func (c *ShopShippingServiceClient) Request(ctx context.Context, req Input) (string, error) {

	fw_method := req.Method

	// Pass on to the real service function
	var err error
	var msg string

	switch fw_method {
	case "GetQuote", "0": // Method 1: GetQuote
		fw_req := pb.GetQuoteRequest{
			Address: &defAddress,
			Items:   []*pb.CartItem{&defCartItem1, &defCartItem2},
		}
		var fw_res *pb.GetQuoteResponse
		fw_res, err = c.client.GetQuote(ctx, &fw_req)
		msg = fmt.Sprintf("req: {Address: %+v, Items: %+v} resp: %+v", &defAddress, []*pb.CartItem{&defCartItem1, &defCartItem2}, fw_res)

	case "ShipOrder", "1": // Method 2: ShipOrder
		fw_req := pb.ShipOrderRequest{
			Address: &defAddress,
			Items:   []*pb.CartItem{&defCartItem1, &defCartItem2},
		}
		var fw_res *pb.ShipOrderResponse
		fw_res, err = c.client.ShipOrder(ctx, &fw_req)
		msg = fmt.Sprintf("req: {Address: %+v, Items: %+v} resp: %+v", &defAddress, []*pb.CartItem{&defCartItem1, &defCartItem2}, fw_res)

	default:
		log.Fatalf("Failed to understand requested method: %s", fw_method)
	}
	if err != nil {
		return "", err
	}

	msg = fmt.Sprintf("method: %s, %s", fw_method, msg)
	// log.Println(msg)
	return msg, nil
}

type ShopShippingServiceGenerator struct {
	GeneratorBase
}

func (g *ShopShippingServiceGenerator) Next() Input {
	return g.defaultInput
}

func (c *ShopShippingServiceClient) GetGenerator() Generator {
	return new(ShopShippingServiceGenerator)
}
