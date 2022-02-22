FROM golang:1.16

WORKDIR /app
COPY go/* /app/

RUN go get . && go build .

ENTRYPOINT /app/server
