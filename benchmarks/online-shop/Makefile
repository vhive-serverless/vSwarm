DOCKER_HUB_ACCOUNT=caldiuoa
FUNCTIONS = adservice cartservice checkoutservice currencyservice emailservice paymentservice productcatalogservice recommendationservice shippingservice
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

ROOT = .

ARCH := $(shell uname -m)

ifeq ($(ARCH),riscv64)
    DOCKERFILE := riscv.Dockerfile
else
    DOCKERFILE := Dockerfile
endif
all: all-image

all-image: $(ALL_IMAGES)

adservice-image: ./adservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-adservice:latest \
	-f ./adservice/$(DOCKERFILE)   \
	$(ROOT)/adservice/

cartservice-image: ./cartservice/src/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-cartservice:latest \
	-f ./cartservice/src/$(DOCKERFILE)   \
	$(ROOT)/cartservice/src/

checkoutservice-image: ./checkoutservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-checkoutservice:latest \
	-f ./checkoutservice/$(DOCKERFILE)   \
	$(ROOT)/checkoutservice/

currencyservice-image: ./currencyservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-currencyservice:latest \
	-f ./currencyservice/$(DOCKERFILE)   \
	$(ROOT)/currencyservice/

emailservice-image: ./emailservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-emailservice:latest \
	-f ./emailservice/$(DOCKERFILE)   \
	$(ROOT)/emailservice/

paymentservice-image: ./paymentservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-paymentservice:latest \
	-f ./paymentservice/$(DOCKERFILE)   \
	$(ROOT)/paymentservice/

productcatalogservice-image: ./productcatalogservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-productcatalogservice:latest \
	-f ./productcatalogservice/$(DOCKERFILE)   \
	$(ROOT)/productcatalogservice/

recommendationservice-image:  ./recommendationservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-recommendationservice:latest \
	-f ./recommendationservice/$(DOCKERFILE)   \
	$(ROOT)/recommendationservice/

shippingservice-image: ./shippingservice/$(DOCKERFILE)  
	DOCKER_BUILDKIT=1 docker build \
	--tag $(DOCKER_HUB_ACCOUNT)/onlineshop-shippingservice:latest \
	-f ./shippingservice/$(DOCKERFILE)   \
	$(ROOT)/shippingservice/

# Push images

push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,onlineshop-,$@):latest

push: $(addprefix push-, $(FUNCTIONS))

# Pull images

pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,onlineshop-,$@):latest

pull: $(addprefix pull-, $(FUNCTIONS))
