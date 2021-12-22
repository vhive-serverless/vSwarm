FROM golang:1.16 AS builder

WORKDIR /app
COPY * /app/
# COPY proto/helloworld.proto /app/proto/

# RUN apt update && apt install -y protobuf-compiler
# RUN go get -u github.com/golang/protobuf/protoc-gen-go
# RUN protoc -I /app/proto /app/proto/helloworld.proto --go_out=plugins=grpc:/app/proto
# RUN go env -w GOPROXY=https://goproxy.cn/,direct && go get . && go build .
RUN go get . && go build .



FROM vhiveease/runner
WORKDIR /app
COPY --from=builder /app/server /app/server

ENTRYPOINT /app/server
