DOCKER_HUB_ACCOUNT=vhiveease
SHELL := /bin/bash

MAKEFILE_NAME := $(lastword $(MAKEFILE_LIST))
UNAME := $(shell whoami)
UID := $(shell id -u `whoami`)
GROUPNAME := $(shell id -gn `whoami`)
GROUPID := $(shell id -g `whoami`)

HOST_VOL ?= ${PWD}
CONTAINER_VOL ?= /workspace

BUILD_DIR := build
DATA_DIR := $(BUILD_DIR)/data
BERT_DIR := $(DATA_DIR)/bert_tf_v1_1_large_fp32_384_v2
RESULT_DIR := $(BUILD_DIR)/result
MLPERF_CONF := $(BUILD_DIR)/mlperf.conf
FEATURE_CACHE := eval_features.pickle

ROOT = ../../

FUNCTIONS = bert-python
ALL_IMAGES = $(addsuffix -image, $(FUNCTIONS))

# Handle different nvidia-docker version
ifneq ($(wildcard /usr/bin/nvidia-docker),)
	DOCKER_RUN_CMD := nvidia-docker run
else
	DOCKER_RUN_CMD := docker run --gpus=all
endif

all: all-image

all-image: $(ALL_IMAGES)

.PHONY: setup
setup:
	@if [ ! -e $(BUILD_DIR) ]; then \
		mkdir $(BUILD_DIR); \
	fi
	@$(MAKE) -f $(MAKEFILE_NAME) download_data
	@$(MAKE) -f $(MAKEFILE_NAME) download_model

.PHONY: download_data
download_data:
	@if [ ! -e $(DATA_DIR) ]; then \
		mkdir $(DATA_DIR); \
	fi
	@if [ ! -e $(DATA_DIR)/dev-v1.1.json ]; then \
		wget -O $(DATA_DIR)/dev-v1.1.json https://github.com/rajpurkar/SQuAD-explorer/blob/master/dataset/dev-v1.1.json?raw=true; \
	fi
	@if [ ! -e $(DATA_DIR)/evaluate-v1.1.py ]; then \
		wget -O $(DATA_DIR)/evaluate-v1.1.py https://github.com/allenai/bi-att-flow/raw/master/squad/evaluate-v1.1.py; \
	fi
	@if [ ! -e $(BERT_DIR) ]; then \
		mkdir $(BERT_DIR) ; \
	fi
	@if [ ! -e $(RESULT_DIR) ]; then \
		mkdir $(RESULT_DIR); \
	fi

.PHONY: download_model
download_model:
	@if [ ! -e $(BERT_DIR)/model.ckpt-5474.data-00000-of-00001 ]; then \
		wget -O $(BERT_DIR)/model.ckpt-5474.data-00000-of-00001 https://zenodo.org/record/3733868/files/model.ckpt-5474.data-00000-of-00001?download=1; \
	fi
	@if [ ! -e $(BERT_DIR)/model.ckpt-5474.index ]; then \
		wget -O $(BERT_DIR)/model.ckpt-5474.index https://zenodo.org/record/3733868/files/model.ckpt-5474.index?download=1; \
	fi
	@if [ ! -e $(BERT_DIR)/model.ckpt-5474.meta ]; then \
		wget -O $(BERT_DIR)/model.ckpt-5474.meta https://zenodo.org/record/3733868/files/model.ckpt-5474.meta?download=1; \
	fi
	@if [ ! -e $(BERT_DIR)/vocab.txt ]; then \
		wget -O $(BERT_DIR)/vocab.txt https://zenodo.org/record/3733868/files/vocab.txt?download=1; \
	fi
	@if [ ! -e $(BERT_DIR)/model.pb ]; then \
		wget -O $(BERT_DIR)/model.pb https://zenodo.org/record/3939747/files/model.pb?download=1; \
	fi
	@if [ ! -e $(BERT_DIR)/model.pytorch ]; then \
		wget -O $(BERT_DIR)/model.pytorch https://zenodo.org/record/3733896/files/model.pytorch?download=1; \
	fi
	@if [ ! -e $(BERT_DIR)/vocab.txt ]; then \
		wget -O $(BERT_DIR)/vocab.txt https://zenodo.org/record/3733896/files/vocab.txt?download=1; \
	fi


# .PHONY: build_docker
# build_docker:
bert-python-image: docker/Dockerfile python/server.py
	@docker pull nvcr.io/nvidia/tensorrtserver:19.08-py3
	DOCKER_BUILDKIT=1 docker buildx build \
		--build-arg GID=$(GROUPID) \
		--build-arg UID=$(UID) \
		--build-arg GROUP=$(GROUPNAME) \
		--build-arg USER=$(UNAME) \
		--build-arg BASE_IMAGE=mlperf-inference-bert \
		--tag $(DOCKER_HUB_ACCOUNT)/bert-python:latest \
		-f docker/Dockerfile \
		$(ROOT) --load
		
		
		

.PHONY: launch_docker
launch_docker:
	$(DOCKER_RUN_CMD) --rm -it -w /workspace $(DOCKER_HUB_ACCOUNT)/bert-python

.PHONY: clean
clean:
	@rm -rf ${BUILD_DIR}

push-%: %-image
	docker push docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst push-,,$@):latest

pull-%:
	docker pull docker.io/$(DOCKER_HUB_ACCOUNT)/$(subst pull-,,$@):latest