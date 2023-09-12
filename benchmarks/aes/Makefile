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

FUNCTIONS = aes-python aes-nodejs aes-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))
ALL_LAMBDA_IMAGES = $(addsuffix -lambda-image, $(FUNCTIONS))

export AWS_REGION := ${AWS_REGION}
export AWS_ACCESS_KEY := ${AWS_ACCESS_KEY}
export AWS_SECRET_KEY := ${AWS_SECRET_KEY}
export AWS_ACCOUNT_ID := ${AWS_ACCOUNT_ID}

all: all-image all-lambda-image

all-image: $(ALL_IMAGES)

all-lambda-image: $(ALL_LAMBDA_IMAGES)

aes-python-image: docker/Dockerfile python/server.py
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag vhiveease/aes-python:latest \
	--target aesPython \
	-f docker/Dockerfile \
	$(ROOT) --load


aes-nodejs-image: docker/Dockerfile nodejs/server.js
	DOCKER_BUILDKIT=1 docker buildx build --progress=plain \
	--tag vhiveease/aes-nodejs:latest \
	--target aesNodeJS \
	-f docker/Dockerfile \
	$(ROOT) --load


aes-go-image: docker/Dockerfile go/server.go
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag vhiveease/aes-go:latest \
	--target aesGo \
	-f docker/Dockerfile \
	$(ROOT) --load


aes-python-lambda-image: docker/Dockerfile.Lambda python/server.py
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/aes-python-lambda:latest \
	--target aesPythonLambda \
	-f docker/Dockerfile.Lambda \
	$(ROOT) --load


aes-nodejs-lambda-image: docker/Dockerfile.Lambda nodejs/server.js
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/aes-nodejs-lambda:latest \
	--target aesNodeJSLambda \
	-f docker/Dockerfile.Lambda \
	$(ROOT) --load


aes-go-lambda-image: docker/Dockerfile.Lambda go/server.go
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/aes-go-lambda:latest \
	--target aesGoLambda \
	-f docker/Dockerfile.Lambda \
	$(ROOT) --load

## Push images

push-%: %-image
	docker push docker.io/vhiveease/$(subst push-,,$@):latest

push-%-lambda: %-lambda-image
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin \
		$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	python $(ROOT)/runner/aws_lambda_scripts/aws_actions.py create_ecr_repo -n $(subst push-,,$@)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS)) $(addprefix push-, $(addsuffix -lambda, $(FUNCTIONS)))

## Pull images from docker hub

pull-%:
	docker pull docker.io/vhiveease/$(subst pull-,,$@):latest

pull-%-lambda:
	docker pull $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS)) $(addprefix pull-, $(addsuffix -lambda, $(FUNCTIONS)))
