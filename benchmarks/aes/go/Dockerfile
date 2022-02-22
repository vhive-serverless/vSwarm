FROM golang:1.16 AS builder

WORKDIR /app
COPY * /app/
RUN go get . && go build .



FROM vhiveease/runner
WORKDIR /app
COPY --from=builder /app/server /app/server

ENTRYPOINT /app/server
