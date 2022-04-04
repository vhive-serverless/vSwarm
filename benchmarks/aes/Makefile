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


clean: clean-proto


ROOT = ../../

.PHONY: proto

FUNCTIONS = aes-python aes-nodejs aes-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

all: all_image

all_image: $(ALL_IMAGES)


aes-python-image: Dockerfile proto/aes_pb2_grpc.py proto/aes_pb2.py python/server.py
	DOCKER_BUILDKIT=1 docker build \
	--tag vhiveease/aes-python:latest \
	--target aesPython \
	-f Dockerfile \
	$(ROOT)


aes-nodejs-image: Dockerfile proto/aes.proto nodejs/server.js
	DOCKER_BUILDKIT=1 docker build --progress=plain \
	--tag vhiveease/aes-nodejs:latest \
	--target aesNodeJS \
	-f Dockerfile \
	$(ROOT)


aes-go-image: Dockerfile proto/aes_grpc.pb.go proto/aes.pb.go go/server.go
	DOCKER_BUILDKIT=1 \
	docker build \
	--tag vhiveease/aes-go:latest \
	--target aesGo \
	-f Dockerfile \
	$(ROOT)


## Push images

push-%: %-image
	docker push docker.io/vhiveease/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS))

## Pull images from docker hub

pull-%:
	docker pull docker.io/vhiveease/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))



## Protocol buffer
proto: proto/_.py proto/_.go

proto/%.py: proto/aes.proto
	python3 -m pip install -r python/requirements.txt
	cd proto && \
	python3 -m grpc_tools.protoc -I. \
		--python_out=. \
		--grpc_python_out=. \
		aes.proto

proto/%.go: proto/aes.proto
	protoc --go_out=. \
		--go_opt=paths=source_relative \
		--go-grpc_out=. \
		--go-grpc_opt=paths=source_relative proto/aes.proto


clean-proto:
	rm -f proto/*.py
	rm -f proto/*.go
