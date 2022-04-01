module grpcclient

go 1.18

replace (
	helloworld/proto => ../proto/helloworld
	hipstershop/proto => ../proto/hipstershop
	hotel_reserv/geo => ../proto/hotel_reserv/geo
	hotel_reserv/profile => ../proto/hotel_reserv/profile
	hotel_reserv/rate => ../proto/hotel_reserv/rate
	hotel_reserv/recommendation => ../proto/hotel_reserv/recommendation
	hotel_reserv/reservation => ../proto/hotel_reserv/reservation
	hotel_reserv/search => ../proto/hotel_reserv/search
	hotel_reserv/user => ../proto/hotel_reserv/user
)

require (
	github.com/sirupsen/logrus v1.8.1
	helloworld/proto v0.0.0-00010101000000-000000000000
	hipstershop/proto v0.0.0-00010101000000-000000000000
	hotel_reserv/geo v0.0.0-00010101000000-000000000000
	hotel_reserv/profile v0.0.0-00010101000000-000000000000
	hotel_reserv/rate v0.0.0-00010101000000-000000000000
	hotel_reserv/recommendation v0.0.0-00010101000000-000000000000
	hotel_reserv/reservation v0.0.0-00010101000000-000000000000
	hotel_reserv/search v0.0.0-00010101000000-000000000000
	hotel_reserv/user v0.0.0-00010101000000-000000000000
)

require (
	github.com/golang/protobuf v1.5.2 // indirect
	golang.org/x/net v0.0.0-20200822124328-c89045814202 // indirect
	golang.org/x/sys v0.0.0-20200323222414-85ca7c5b95cd // indirect
	golang.org/x/text v0.3.0 // indirect
	google.golang.org/genproto v0.0.0-20200526211855-cb27e3aa2013 // indirect
	google.golang.org/grpc v1.45.0 // indirect
	google.golang.org/protobuf v1.28.0 // indirect
)
