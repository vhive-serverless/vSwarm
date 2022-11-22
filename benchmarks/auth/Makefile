DOCKER_HUB_ACCOUNT=vhiveease
FUNCTIONS = auth-python auth-nodejs auth-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

clean: clean-proto

ROOT = ../../

all: all_image

all_image: $(ALL_IMAGES)



auth-python-image: docker/Dockerfile python/server.py
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-python:latest \
	--target authPython \
	-f docker/Dockerfile \
	$(ROOT)


auth-nodejs-image: docker/Dockerfile nodejs/server.js
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-nodejs:latest \
	--target authNodeJS \
	-f docker/Dockerfile \
	$(ROOT)


auth-go-image: docker/Dockerfile go/server.go
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-go:latest \
	--target authGo \
	-f docker/Dockerfile \
	$(ROOT)





push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS))


pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))
