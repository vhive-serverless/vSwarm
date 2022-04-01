package main

import (
	log "github.com/sirupsen/logrus"
	. "relay/clients"
)

// helloworld "google.golang.org/grpc/examples/helloworld/helloworld"
// helloworld "github.com/ease-lab/serverless-perf/go-helper-lib/protos/helloworld"

// // ------ gRPC Client interface ------
// // Every client must implement this interface
// type GrpcClient interface {
// 	Init(ip, port string)
// 	Request(req string) string
// 	Close()
// }

func FindServiceName(functionName string) string {
	switch functionName {
	case "aes-go", "aes-python", "aes-nodejs":
		return "helloworld"
	case "auth-go", "auth-python", "auth-nodejs":
		return "helloworld"
	case "fibonacci-go", "fibonacci-python", "fibonacci-nodejs":
		return "helloworld"
	default:
		return functionName
	}
}

// Helper to find a grpc client for the given service
func FindGrpcClient(service_name string) GrpcClient {
	switch service_name {
	case "helloworld":
		log.Info("Found Helloworld client")
		return new(HelloWorldClient)

		// Hotel reservation ---
	case "Geo", "geo":
		log.Info("Found geo client")
		return new(HotelGeoClient)
	case "Profile", "profile":
		log.Info("Found profile client")
		return new(HotelProfileClient)
	case "Rate", "rate":
		log.Info("Found rate client")
		return new(HotelRateClient)
	case "Recommendation", "recommendation":
		log.Info("Found recommendation client")
		return new(HotelRecommendationClient)
	case "Reservation", "reservation":
		log.Info("Found reservation client")
		return new(HotelReservationClient)
	case "User", "user":
		log.Info("Found user client")
		return new(HotelUserClient)
	case "Search", "search":
		log.Info("Found search client")
		return new(HotelSearchClient)

		// Hipster shop ---
	case "Ad", "adservice":
		log.Info("Found Ad client for online shop")
		return new(ShopAdServiceClient)
	case "Cart", "cartservice":
		log.Info("Found Cart client for online shop")
		return new(ShopCartServiceClient)
	case "Checkout", "checkoutservice":
		log.Info("Found Checkout client for online shop")
		return new(ShopCheckoutServiceClient)
	case "Currency", "currencyservice":
		log.Info("Found Currency client for online shop")
		return new(ShopCurrencyServiceClient)
	case "Email", "emailservice":
		log.Info("Found Email client for online shop")
		return new(ShopEmailServiceClient)
	case "Payment", "paymentservice":
		log.Info("Found Payment client for online shop")
		return new(ShopPaymentServiceClient)
	case "ProductCatalog", "productcatalogservice":
		log.Info("Found ProductCatalog client for online shop")
		return new(ShopProductCatalogServiceClient)
	case "recommendationservice":
		log.Info("Found Recommendation client for online shop")
		return new(ShopRecommendationServiceClient)
	case "Shipping", "shippingservice":
		log.Info("Found Shipping client for online shop")
		return new(ShopShippingServiceClient)

	// Default ---------
	default:
		log.Warnf("Did not find a matching client for %s... Will use the default Hello world client. \n", service_name)
		return new(HelloWorldClient)
	}
}
