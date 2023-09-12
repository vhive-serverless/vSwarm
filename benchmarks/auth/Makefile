
DOCKER_HUB_ACCOUNT=vhiveease
FUNCTIONS = auth-python auth-nodejs auth-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))
ALL_LAMBDA_IMAGES = $(addsuffix -lambda-image, $(FUNCTIONS))

export AWS_REGION := ${AWS_REGION}
export AWS_ACCESS_KEY := ${AWS_ACCESS_KEY}
export AWS_SECRET_KEY := ${AWS_SECRET_KEY}
export AWS_ACCOUNT_ID := ${AWS_ACCOUNT_ID}

clean: clean-proto

ROOT = ../../

all: all-image all-lambda-image

all-image: $(ALL_IMAGES)

all-lambda-image: $(ALL_LAMBDA_IMAGES)

auth-python-image: docker/Dockerfile python/server.py
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-python:latest \
	--target authPython \
	-f docker/Dockerfile \
	$(ROOT) --load


auth-nodejs-image: docker/Dockerfile nodejs/server.js
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-nodejs:latest \
	--target authNodeJS \
	-f docker/Dockerfile \
	$(ROOT) --load


auth-go-image: docker/Dockerfile go/server.go
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-go:latest \
	--target authGo \
	-f docker/Dockerfile \
	$(ROOT) --load


auth-python-lambda-image: docker/Dockerfile.Lambda python/server.py
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/auth-python-lambda:latest \
	--target authPythonLambda \
	-f docker/Dockerfile.Lambda \
	$(ROOT) --load

auth-python-lambda-image: docker/Dockerfile.Lambda python/server.py
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/auth-python-lambda:latest \
	--target authPythonLambda \
	-f docker/Dockerfile.Lambda \
	$(ROOT) --load

auth-nodejs-lambda-image: docker/Dockerfile.Lambda nodejs/server.js
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/auth-nodejs-lambda:latest \
	--target authNodeJSLambda \
	-f docker/Dockerfile.Lambda \
	$(ROOT) --load


auth-go-lambda-image: docker/Dockerfile.Lambda go/server.go
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/auth-go-lambda:latest \
	--target authGoLambda \
	-f docker/Dockerfile.Lambda \
	$(ROOT) --load


push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@):latest

push-%-lambda: %-lambda-image
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin \
		$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	python $(ROOT)/runner/aws_lambda_scripts/aws_actions.py create_ecr_repo -n $(subst push-,,$@)
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS)) $(addprefix push-, $(addsuffix -lambda, $(FUNCTIONS)))


pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@):latest

pull-%-lambda:
	docker pull $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS)) $(addprefix pull-, $(addsuffix -lambda, $(FUNCTIONS)))
