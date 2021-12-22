# MIT License
#
# Copyright (c) 2021 David Schall and EASE lab
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

# all: all-image

# all-image: producer-image consumer-image driver-image

# all-image-push: producer-image-push consumer-image-push driver-image-push

# clean:
# 	rm -f ./producer-bin ./consumer-bin


# producer-image: Dockerfile producer/producer.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
# 	DOCKER_BUILDKIT=1 docker build \
# 	--tag vhiveease/chained-functions-serving-producer:latest \
# 	--build-arg target_arg=producer \
# 	--secret id=GOPRIVATE_KEY \
# 	-f Dockerfile ../..

# producer-image-push: producer-image
# 	docker push vhiveease/chained-functions-serving-producer:latest


# consumer-image: Dockerfile consumer/consumer.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
# 	DOCKER_BUILDKIT=1 docker build \
# 	--tag vhiveease/chained-functions-serving-consumer:latest \
# 	--build-arg target_arg=consumer \
# 	--secret id=GOPRIVATE_KEY \
# 	-f Dockerfile ../..


# consumer-image-push: consumer-image
# 	docker push vhiveease/chained-functions-serving-consumer:latest

# driver-image: Dockerfile driver/driver.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
# 	DOCKER_BUILDKIT=1 docker build \
# 	--tag vhiveease/chained-functions-serving-driver:latest \
# 	--build-arg target_arg=driver \
# 	--secret id=GOPRIVATE_KEY \
# 	-f Dockerfile ../..

# driver-image-push: driver-image
# 	docker push vhiveease/chained-functions-serving-driver:latest

# cmd/server/tempReader_grpc.pb.go cmd/server/tempReader.pb.go: cmd/server/tempReader.proto
# 	protoc \
# 		--go_out=. \
# 		--go_opt="paths=source_relative" \
# 		--go-grpc_out=. \
# 		--go-grpc_opt="paths=source_relative" \
# 		cmd/server/tempReader.proto


# all: all-image

all-image: aes-python-image

# all-image-push: producer-image-push consumer-image-push driver-image-push

# clean:
# 	rm -f ./producer-bin ./consumer-bin
DOCKER_HUB_ACCOUNT=davidschall


FUNCTIONS = aes-python aes-nodejs aes-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))



aes-python-image:
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/aes-python:latest \
	-f ./python/Dockerfile.python python/


aes-nodejs-image:
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/aes-nodejs:latest \
	-f ./nodejs/Dockerfile nodejs/

aes-go-image:
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/aes-go:latest \
	-f ./go/Dockerfile go/



# push: aes-python-image
# 	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$<:latest

push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS))


pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))


# BUCKET = ${AWS_TEST_BUCKET}
# BIN_DIR = ./bin
# PROG_NAME = word_count

# .PHONY: all clean $(PROG_NAME) input_in_s3 push

# all: $(PROG_NAME)

# $(PROG_NAME):
# 	go build -o $(BIN_DIR)/$@ .

# input_in_s3:
# 	aws s3 cp ./metamorphosis.txt s3://${BUCKET}

# push:
# 	docker build --tag docker.io/vhiveease/word_count:local -f ./Dockerfile ../..
# 	docker push docker.io/vhiveease/word_count:local

# test_wc_local: $(PROG_NAME)
# 	$(BIN_DIR)/$(PROG_NAME) metamorphosis.txt

# test_wc_s3: $(PROG_NAME) input_in_s3
# 	$(BIN_DIR)/$(PROG_NAME) --out s3://${BUCKET}/ s3://${BUCKET}/metamorphosis.txt

# test_wc_lambda: $(PROG_NAME) input_in_s3
# 	$(BIN_DIR)/$(PROG_NAME) --lambda --out s3://${BUCKET}/ s3://${BUCKET}/metamorphosis.txt

# clean:
# 	find . -name "*.out" -print0 | xargs -0 rm
# 	rm -f $(BIN_DIR)/$(PROG_NAME) output*
# 	aws s3 rm s3://${BUCKET} --recursive


# producer-image: Dockerfile producer/producer.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
# 	DOCKER_BUILDKIT=1 docker build \
# 	--tag vhiveease/chained-functions-serving-producer:latest \
# 	--build-arg target_arg=producer \
# 	--secret id=GOPRIVATE_KEY \
# 	-f Dockerfile ../..

# producer-image-push: producer-image
# 	docker push vhiveease/chained-functions-serving-producer:latest


# consumer-image: Dockerfile consumer/consumer.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
# 	DOCKER_BUILDKIT=1 docker build \
# 	--tag vhiveease/chained-functions-serving-consumer:latest \
# 	--build-arg target_arg=consumer \
# 	--secret id=GOPRIVATE_KEY \
# 	-f Dockerfile ../..


# consumer-image-push: consumer-image
# 	docker push vhiveease/chained-functions-serving-consumer:latest

# driver-image: Dockerfile driver/driver.go proto/prodcon.pb.go proto/prodcon_grpc.pb.go
# 	DOCKER_BUILDKIT=1 docker build \
# 	--tag vhiveease/chained-functions-serving-driver:latest \
# 	--build-arg target_arg=driver \
# 	--secret id=GOPRIVATE_KEY \
# 	-f Dockerfile ../..

# driver-image-push: driver-image
# 	docker push vhiveease/chained-functions-serving-driver:latest

# cmd/server/tempReader_grpc.pb.go cmd/server/tempReader.pb.go: cmd/server/tempReader.proto
# 	protoc \
# 		--go_out=. \
# 		--go_opt="paths=source_relative" \
# 		--go-grpc_out=. \
# 		--go-grpc_opt="paths=source_relative" \
# 		cmd/server/tempReader.proto