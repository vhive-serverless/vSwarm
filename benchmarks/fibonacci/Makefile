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
FUNCTIONS = fibonacci-python fibonacci-nodejs fibonacci-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

clean: clean-proto

ROOT = ../../

all: all-image

all-image: $(ALL_IMAGES)

fibonacci-python-image:  Dockerfile python/server.py
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-python-mod:latest \
	--target fibonacciPython \
	-f ./Dockerfile \
	$(ROOT)


fibonacci-nodejs-image: Dockerfile nodejs/server.js
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-nodejs-mod:latest \
	--target fibonacciNodeJS \
	-f ./Dockerfile \
	$(ROOT)

fibonacci-go-image: Dockerfile go/server.go
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-go-mod:latest \
	--target fibonacciGo \
	-f ./Dockerfile \
	$(ROOT)


push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@)-mod:latest

push: $(addprefix push-, $(FUNCTIONS))


pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@)-mod:latest

pull: $(addprefix pull-, $(FUNCTIONS))
