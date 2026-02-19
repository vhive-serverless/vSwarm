package grpcclient

import (
	log "github.com/sirupsen/logrus"
)

func FindServiceName(functionName string) string {
	switch functionName {
	case "aes-go", "aes-python", "aes-nodejs":
		return "aes"
	case "auth-go", "auth-python", "auth-nodejs":
		return "auth"
	case "fibonacci-go", "fibonacci-python", "fibonacci-nodejs", "fibonacci-cpp":
		return "fibonacci"
	case "compression-python":
		return "compression"
	case "gptj-python":
		return "gptj"
	case "image-rotate-python", "image-rotate-nodejs", "image-rotate-go", "image-rotate-cython":
		return "image-rotate"
	case "video-processing-python":
		return "video-processing"
	case "rnn-serving-python":
		return "rnn-serving"
	case "video-analytics-standalone-python":
		return "video-analytics-standalone"
	case "spright-parking-python":
		return "spright-parking"
	case "bert-python":
		return "bert"
	default:
		return functionName
	}
}

// Helper to find a grpc client for the given service
func FindGrpcClient(service_name string) GrpcClient {
	switch service_name {
	case "helloworld":
		log.Debug("Found Helloworld client")
		return new(HelloWorldClient)

	case "aes":
		log.Debug("Found AES client")
		return new(AesClient)
	case "auth":
		log.Debug("Found Auth client")
		return new(AuthClient)
	case "fibonacci":
		log.Debug("Found Fibonacci client")
		return new(FibonacciClient)
	case "compression":
		log.Debug("Found Compression client")
		return new(FileCompressClient)
	case "bert":
		log.Debug("Found Bert client")
		return new(BertClient)
	case "gptj":
		log.Debug("Found gptj client")
		return new(GptJClient)
	case "image-rotate":
		log.Debug("Found image rotate client")
		return new(ImageRotateClient)
	case "video-processing":
		log.Debug("Found video processing client")
		return new(VideoProcessingClient)
	case "rnn-serving":
		log.Debug("Found rnn serving client")
		return new(RNNServingClient)
	case "video-analytics-standalone":
		log.Debug("Found video analytics standalone client")
		return new(VideoAnalyticsClient)

		// Hotel reservation ---
	case "Geo", "geo":
		log.Debug("Found geo client")
		return new(HotelGeoClient)
	case "Profile", "profile":
		log.Debug("Found profile client")
		return new(HotelProfileClient)
	case "Rate", "rate":
		log.Debug("Found rate client")
		return new(HotelRateClient)
	case "Recommendation", "recommendation":
		log.Debug("Found recommendation client")
		return new(HotelRecommendationClient)
	case "Reservation", "reservation":
		log.Debug("Found reservation client")
		return new(HotelReservationClient)
	case "User", "user":
		log.Debug("Found user client")
		return new(HotelUserClient)
	case "Search", "search":
		log.Debug("Found search client")
		return new(HotelSearchClient)

	// Hipster shop ---
	case "Ad", "adservice":
		log.Debug("Found Ad client for online shop")
		return new(ShopAdServiceClient)
	case "Cart", "cartservice":
		log.Debug("Found Cart client for online shop")
		return new(ShopCartServiceClient)
	case "Checkout", "checkoutservice":
		log.Debug("Found Checkout client for online shop")
		return new(ShopCheckoutServiceClient)
	case "Currency", "currencyservice":
		log.Debug("Found Currency client for online shop")
		return new(ShopCurrencyServiceClient)
	case "Email", "emailservice":
		log.Debug("Found Email client for online shop")
		return new(ShopEmailServiceClient)
	case "Payment", "paymentservice":
		log.Debug("Found Payment client for online shop")
		return new(ShopPaymentServiceClient)
	case "ProductCatalog", "productcatalogservice":
		log.Debug("Found ProductCatalog client for online shop")
		return new(ShopProductCatalogServiceClient)
	case "recommendationservice":
		log.Debug("Found Recommendation client for online shop")
		return new(ShopRecommendationServiceClient)
	case "Shipping", "shippingservice":
		log.Debug("Found Shipping client for online shop")
		return new(ShopShippingServiceClient)

	// Spright parking ---
	case "spright-parking":
		log.Debug("Found Spright client for spright parking")
		return new(ParkingClient)

	// Default ---------
	default:
		log.Warnf("Did not find a matching client for %s... Will use the default Hello world client. \n", service_name)
		return new(HelloWorldClient)
	}
}
