# MIT License
#
# Copyright (c) 2021 Michal Baczun and EASE lab
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

all: all-image-push

all-image: driver-fibonacci-image driver-llvm-image driver-excamera-image

all-image-push: gg-driver-fibonacci-image-push gg-driver-llvm-image-push gg-driver-excamera-image-push

driver-fibonacci-image: Dockerfile
	DOCKER_BUILDKIT=1 docker build --tag vhiveease/gg-driver-fibonacci:latest --build-arg target_arg=fibonacci .

driver-llvm-image: Dockerfile
	DOCKER_BUILDKIT=1 docker build --tag vhiveease/gg-driver-llvm:latest --build-arg target_arg=llvm .

driver-excamera-image: Dockerfile
	DOCKER_BUILDKIT=1 docker build --tag vhiveease/gg-driver-excamera:latest --build-arg target_arg=excamera .

gg-driver-fibonacci-image-push: driver-fibonacci-image
	docker push vhiveease/gg-driver-fibonacci:latest

gg-driver-llvm-image-push: driver-llvm-image
	docker push vhiveease/gg-driver-llvm:latest

gg-driver-excamera-image-push: driver-excamera-image
	docker push vhiveease/gg-driver-excamera:latest