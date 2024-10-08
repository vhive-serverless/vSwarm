# MIT License

# Copyright (c) 2024 EASE lab

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

ROOT = ../../
FUNCTIONS = compression-python init-database
ALL_IMAGES = $(FUNCTIONS)

all-image: $(ALL_IMAGES)

compression-python: Dockerfile python/server.py python/requirements.txt files/metamorphosis.txt
	DOCKER_BUILDKIT=1 docker build \
	--tag vhiveease/compression-python:latest \
	--target compressionPython \
	-f ./Dockerfile \
	$(ROOT) --load

init-database: Dockerfile init/init-database.go files/metamorphosis.txt
	DOCKER_BUILDKIT=1 docker build \
	--tag vhiveease/compression-init-database:latest \
	--target databaseInit \
	-f ./Dockerfile \
	$(ROOT) --load

## Push images
push:
	docker push docker.io/vhiveease/compression-python:latest 
	docker push docker.io/vhiveease/compression-init-database:latest

## Pull images from docker hub
pull:
	docker pull docker.io/vhiveease/compression-python:latest
	docker pull docker.io/vhiveease/compression-init-database:latest
