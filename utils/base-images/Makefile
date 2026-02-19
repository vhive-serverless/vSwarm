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


.PHONY: all

IMAGES 	  ?= golang-builder golang python-slim node-slim mongodb memcached go-alpine-base \
python3.10-grpc-only-1.71 python3.10-runner node-jammy-base node-alpine-runner \
python-debian-base-grpc-only debian-trixie cassandra java-17-runner java-17-builder \
noble-base redis python3.11-trixie python3.11-trixie-runner python-debian-base-with-grpcio-tools


DOCKER_HUB_ACCOUNT=caldiuoa


ARCH := $(shell uname -m)
ifeq ($(ARCH),riscv64)
    DOCKERFILE := riscv.Dockerfile
else
    DOCKERFILE := Dockerfile
endif


python3.10-grpc-only-1.71 : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.10-grpc-only-1.71 \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-python3.10-grpc-only-1.71 : python3.10-grpc-only-1.71
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.10-grpc-only-1.71

python3.10-runner : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.10-runner \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-python3.10-runner: python3.10-runner
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.10-runner 



python3.11-trixie : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.11-trixie \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-python3.11-trixie: python3.11-trixie
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.11-trixie 



python3.11-trixie-runner  : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.11-trixie-runner  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-python3.11-trixie-runner : python3.11-trixie-runner 
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:3.11-trixie-runner  


go-alpine-base : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/go-base:1.21-riscv64 \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-go-alpine-base : go-alpine-base 
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/go-base:1.21-riscv64 

node-jammy-base : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/node-base:jammy-builder  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-node-jammy-base : node-jammy-base
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/node-base:jammy-builder

node-alpine-runner : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/node-base:alpine-runner  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-node-alpine-runner : node-alpine-runner
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/node-base:alpine-runner



python-debian-base-with-grpcio-tools : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:debian_grpcio_tools_riscv64  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-python-debian-base-with-grpcio-tools : python-debian-base-with-grpcio-tools
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:debian_grpcio_tools_riscv64

python-debian-base-grpc-only : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:debian_grpc_only_riscv64  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-python-debian-base-grpc-only : python-debian-base-grpc-only
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/python-base:debian_grpc_only_riscv64


debian-trixie : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/debian-base:trixie  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-debian-trixie : debian-trixie
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/debian-base:trixie

cassandra : ./cassandra/Dockerfile
	docker build -f ./cassandra/Dockerfile -t $(DOCKER_HUB_ACCOUNT)/cassandra:latest .


push-cassandra : cassandra
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/cassandra:latest


memcached : ./memcached/Dockerfile
	docker build -f ./memcached/Dockerfile -t $(DOCKER_HUB_ACCOUNT)/memcached:latest .


push-memcached : memcached
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/memcached:latest


java-17-builder : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/java-builder:17  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-java-17-builder : java-17-builder
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/java-builder:17

java-17-runner : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/java-runner:17  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-java-17-runner : java-17-runner
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/java-runner:17


noble-base : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/noble-base:latest  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-noble-base : noble-base
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/noble-base:latest


redis : riscv.Dockerfile
	DOCKER_BUILDKIT=1 docker build \
	--tag docker.io/$(DOCKER_HUB_ACCOUNT)/redis:latest  \
	--target $@ \
	-f riscv.Dockerfile \
	.

push-redis : redis
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/redis:latest


all: $(IMAGES)





# docker build -f ./Dockerfile . --tag pourpourr/cassandra:latest
