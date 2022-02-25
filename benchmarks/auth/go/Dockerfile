## First stage:
## Builder
FROM golang:1.16 AS builder

WORKDIR /app
COPY . .

RUN go get .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo .


## Second stage: deployment image
FROM alpine:3.14
RUN apk --no-cache add ca-certificates

LABEL author="David Schall"

WORKDIR /app/
COPY --from=builder /app/server .

ENTRYPOINT /app/server
