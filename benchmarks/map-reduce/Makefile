# MIT License
#
# Copyright (c) 2021 Dmitrii Ustiugov and EASE lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

ROOT = ../../
HERE = ./benchmarks/map-reduce

PLATFORM = --platform linux/amd64
MODE = --load

export AWS_REGION := ${AWS_REGION}
export AWS_ACCESS_KEY := ${AWS_ACCESS_KEY}
export AWS_SECRET_KEY := ${AWS_SECRET_KEY}
export AWS_ACCOUNT_ID := ${AWS_ACCOUNT_ID}

# For debugging on Apple M1 below
#PLATFORM = --platform linux/arm64
#MODE = --push

.PHONY: proto

all: all-image all-image-lambda

all-image: driver-image mapper-image reducer-image

all-image-lambda: driver-image-lambda mapper-image-lambda reducer-image-lambda

all-push: all-image-push all-image-lambda-push

all-image-push: driver-image-push mapper-image-push reducer-image-push

all-image-lambda-push: driver-image-lambda-push mapper-image-lambda-push reducer-image-lambda-push

driver-image: docker/Dockerfile proto/mapreduce_pb2_grpc.py proto/mapreduce_pb2.py driver/main.py
	docker buildx build $(PLATFORM) \
	-t vhiveease/mapreduce-driver:latest \
	--build-arg target_arg=driver \
	--secret id=GOPRIVATE_KEY \
	-f docker/Dockerfile \
	$(ROOT) $(MODE)

mapper-image: docker/Dockerfile proto/mapreduce_pb2_grpc.py proto/mapreduce_pb2.py mapper/main.py
	docker buildx build $(PLATFORM) \
	-t vhiveease/mapreduce-mapper:latest \
	--build-arg target_arg=mapper \
	--secret id=GOPRIVATE_KEY \
	-f docker/Dockerfile \
	$(ROOT) $(MODE)

reducer-image: docker/Dockerfile proto/mapreduce_pb2_grpc.py proto/mapreduce_pb2.py reducer/main.py
	docker buildx build $(PLATFORM) \
	-t vhiveease/mapreduce-reducer:latest \
	--build-arg target_arg=reducer \
	--secret id=GOPRIVATE_KEY \
	-f docker/Dockerfile \
	$(ROOT) $(MODE)

driver-image-lambda: docker/Dockerfile.Lambda driver/main.py
	docker buildx build $(PLATFORM) \
	-t $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/mapreduce-driver-lambda:latest \
	--build-arg target_arg=driver \
	-f docker/Dockerfile.Lambda \
	$(ROOT) $(MODE)

mapper-image-lambda: docker/Dockerfile.Lambda mapper/main.py
	docker buildx build $(PLATFORM) \
	-t $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/mapreduce-mapper-lambda:latest \
	--build-arg target_arg=mapper \
	-f docker/Dockerfile.Lambda \
	$(ROOT) $(MODE)

reducer-image-lambda: docker/Dockerfile.Lambda reducer/main.py
	docker buildx build $(PLATFORM) \
	-t $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/mapreduce-reducer-lambda:latest \
	--build-arg target_arg=reducer \
	-f docker/Dockerfile.Lambda \
	$(ROOT) $(MODE)

driver-image-push: driver-image
	docker push vhiveease/mapreduce-driver:latest

mapper-image-push: mapper-image
	docker push vhiveease/mapreduce-mapper:latest

reducer-image-push: reducer-image
	docker push vhiveease/mapreduce-reducer:latest

driver-image-lambda-push: driver-image-lambda
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin \
		$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	python $(ROOT)/runner/aws_lambda_scripts/aws_actions.py create_ecr_repo -n mapreduce-driver-lambda
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/mapreduce-driver-lambda:latest

mapper-image-lambda-push: mapper-image-lambda
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin \
		$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	python $(ROOT)/runner/aws_lambda_scripts/aws_actions.py create_ecr_repo -n mapreduce-mapper-lambda
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/mapreduce-mapper-lambda:latest

reducer-image-lambda-push: reducer-image-lambda
	aws ecr get-login-password --region $(AWS_REGION) | \
		docker login --username AWS --password-stdin \
		$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
	python $(ROOT)/runner/aws_lambda_scripts/aws_actions.py create_ecr_repo -n mapreduce-reducer-lambda
	docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/mapreduce-reducer-lambda:latest

proto: proto/mapreduce.proto proto/helloworld.proto
	python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/mapreduce.proto
	python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/helloworld.proto
