# MIT License

# Copyright (c) 2022 EASE lab

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

DOCKER_HUB_ACCOUNT=vhiveease
FUNCTIONS = fibonacci-python fibonacci-nodejs fibonacci-go fibonacci-cpp
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

clean: clean-proto

ROOT = ../../

.PHONY: proto

all: all_image

all_image: $(ALL_IMAGES)

fibonacci-python-image:  Dockerfile proto/fibonacci_pb2_grpc.py proto/fibonacci_pb2.py python/server.py
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-python:latest \
	--target fibonacciPython \
	-f ./Dockerfile \
	$(ROOT)


fibonacci-nodejs-image: Dockerfile proto/fibonacci.proto nodejs/server.js
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-nodejs:latest \
	--target fibonacciNodeJS \
	-f ./Dockerfile \
	$(ROOT)

fibonacci-go-image: Dockerfile proto/fibonacci_grpc.pb.go proto/fibonacci.pb.go go/server.go
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-go:latest \
	--target fibonacciGo \
	-f ./Dockerfile \
	$(ROOT)
	
fibonacci-cpp-image: Dockerfile proto/fibonacci.proto cpp/main.cpp
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-cpp:latest \
	--target fibonacciCPP \
	-f ./Dockerfile \
	$(ROOT)


push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS))


pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))

## Protocol buffer
proto: proto/_.py proto/_.go

proto/%.py: proto/fibonacci.proto
	pip install -r python/requirements.txt
	cd proto && \
	python3 -m grpc_tools.protoc -I. \
		--python_out=. \
		--grpc_python_out=. \
		fibonacci.proto

proto/%.go: proto/fibonacci.proto
	protoc --go_out=. \
		--go_opt=paths=source_relative \
		--go-grpc_out=. \
		--go-grpc_opt=paths=source_relative proto/fibonacci.proto


clean-proto:
	rm -f proto/*.py
	rm -f proto/*.go