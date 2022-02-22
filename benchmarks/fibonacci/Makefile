DOCKER_HUB_ACCOUNT=vhiveease
FUNCTIONS = fibonacci-python fibonacci-nodejs fibonacci-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

all: all_image

all_image: $(ALL_IMAGES)

fibonacci-python-image:
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-python:latest \
	-f ./python/Dockerfile .


fibonacci-nodejs-image:
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-nodejs:latest \
	-f ./nodejs/Dockerfile .

fibonacci-go-image:
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/fibonacci-go:latest \
	-f ./go/Dockerfile .


push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS))


pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))

