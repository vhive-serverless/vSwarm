# MIT License
#
# Copyright (c) 2021 Michal Baczun and EASE lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Define a Makefile variable using a ENV variable or a default value
# https://stackoverflow.com/a/24264930/4466589
PRODUCER_TAG ?= "vhiveease/chained-functions-serving-producer:latest"
CONSUMER_TAG ?= "vhiveease/chained-functions-serving-consumer:latest"

all: all-image

all-image: producer-image consumer-image

all-image-push: producer-image-push consumer-image-push

clean:
	rm -f ./producer-bin ./consumer-bin


producer-image: Dockerfile producer/producer.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
	buildah build-using-dockerfile --tag $(PRODUCER_TAG) --build-arg target_arg=producer -f Dockerfile ../..

producer-image-push: producer-image
	buildah push --tls-verify=false $(PRODUCER_TAG)


consumer-image: Dockerfile consumer/consumer.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
	buildah build-using-dockerfile --tag $(CONSUMER_TAG) --build-arg target_arg=consumer -f Dockerfile ../..

consumer-image-push: consumer-image
	buildah push --tls-verify=false $(CONSUMER_TAG)


cmd/server/tempReader.pb.go: cmd/server/tempReader.proto
	protoc \
		--go_out=. \
		--go_opt="paths=source_relative" \
		cmd/server/tempReader.proto

cmd/server/tempReader_grpc.pb.go: cmd/server/tempReader.proto
	protoc \
		--go-grpc_out=. \
		--go-grpc_opt="paths=source_relative" \
		cmd/server/tempReader.proto
