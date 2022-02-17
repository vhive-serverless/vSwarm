FROM golang:1.16

WORKDIR /app
COPY go/* /app/
# COPY proto/helloworld.proto /app/proto/

# RUN apt update && apt install -y protobuf-compiler
# RUN go get -u github.com/golang/protobuf/protoc-gen-go
# RUN protoc -I /app/proto /app/proto/helloworld.proto --go_out=plugins=grpc:/app/proto
RUN go get . && go build .

ENTRYPOINT /app/server
