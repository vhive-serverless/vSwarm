ROOT = ../../

FUNCTIONS = parking-python
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

all: all-image

all-image: $(ALL_IMAGES)

parking-python-image: docker/Dockerfile python/server.py
	DOCKER_BUILDKIT=1 docker buildx build \
	--tag vhiveease/parking-python:latest \
	--target parkingPython \
	-f docker/Dockerfile \
	$(ROOT) --load

push-%: %-image
	docker push docker.io/vhiveease/$(subst push-,,$@):latest

pull-%:
	docker pull docker.io/vhiveease/$(subst pull-,,$@):latest

clean:
	@rm -rf build