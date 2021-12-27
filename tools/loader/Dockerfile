# syntax=docker/dockerfile:1.2.x

# Stage 0: builder #
# Use the official Golang image to create a build artifact.
# This is based on Debian and sets the GOPATH to /go.
FROM golang:1.17 as builder

# Create and change to the app directory.
WORKDIR /app

# Retrieve application dependencies using go modules.
# Allows container builds to reuse downloaded dependencies.
COPY go.* ./
RUN go mod download

# Copy local code to the container image.
COPY . ./

# Build the binary.
WORKDIR /app/server/trace-func-go
# -mod=readonly: ensures immutable go.mod and go.sum in container builds.
# CGO_ENABLED=0: avoid using common libraries are found on most major OS distributions.
RUN CGO_ENABLED=0 GOOS=linux go build -mod=readonly -v -o server

# Stage 1: Run #
# Use the official Alpine image for a lean production container.
# https://hub.docker.com/_/alpine
# https://docs.docker.com/develop/develop-images/multistage-build/#use-multi-stage-builds
FROM alpine:3
RUN apk add --no-cache ca-certificates

# Copy the binary to the production image from the builder stage.
COPY --from=builder /app/server/trace-func-go/server /server

# Run the web service on container startup.
CMD ["/server"]