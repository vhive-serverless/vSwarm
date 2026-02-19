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

DOCKER_HUB_ACCOUNT=caldiuoa

ARCH := $(shell uname -m)

ifeq ($(ARCH),riscv64)
    DOCKERFILE := riscv.Dockerfile
else
    DOCKERFILE := Dockerfile
endif

.PHONY: geo profile rate recommendation reservation user search

FUNCTIONS = geo profile rate recommendation reservation user search

ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

all: all-image
all-image: $(ALL_IMAGES)




%-image: $(DOCKERFILE) go.mod %/*
	$(eval func := $(subst -image,,$@))
	DOCKER_BUILDKIT=1 \
	docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/hotel-app-$(func):latest \
	--build-arg SERVICE=$(func) \
	-f $(DOCKERFILE) \
	$(ROOT)



## Push images
push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/hotel-app-$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS))

## Pull images from docker hub
pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/hotel-app-$(subst push-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))

