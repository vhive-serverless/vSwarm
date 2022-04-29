DOCKER_HUB_ACCOUNT=vhiveease
FUNCTIONS = auth-python auth-nodejs auth-go
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

clean: clean-proto

ROOT = ../../

.PHONY: proto

all: all_image

all_image: $(ALL_IMAGES)



auth-python-image: Dockerfile proto/auth_pb2_grpc.py proto/auth_pb2.py python/server.py
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-python:latest \
	--target authPython \
	-f Dockerfile \
	$(ROOT)


auth-nodejs-image: Dockerfile proto/auth.proto nodejs/server.js
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-nodejs:latest \
	--target authNodeJS \
	-f Dockerfile \
	$(ROOT)


auth-go-image: Dockerfile proto/auth_grpc.pb.go proto/auth.pb.go go/server.go
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/auth-go:latest \
	--target authGo \
	-f Dockerfile \
	$(ROOT)





push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@):latest

push: $(addprefix push-, $(FUNCTIONS))


pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))




## Protocol buffer
proto: proto/_.py proto/_.go

proto/%.py: proto/auth.proto
	pip install -r python/requirements.txt
	cd proto && \
	python3 -m grpc_tools.protoc -I. \
		--python_out=. \
		--grpc_python_out=. \
		auth.proto

proto/%.go: proto/auth.proto
	protoc --go_out=. \
		--go_opt=paths=source_relative \
		--go-grpc_out=. \
		--go-grpc_opt=paths=source_relative proto/auth.proto


clean-proto:
	rm -f proto/*.py
	rm -f proto/*.go
