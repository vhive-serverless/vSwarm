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

#---------- Init-Database -----------#
# First stage (Builder):
FROM  --platform=riscv64  caldiuoa/go-base:1.21-riscv64 AS databaseInitBuilder
WORKDIR /app/app/
USER root
RUN apk add --no-cache ca-certificates git
RUN apk add build-base
# RUN apt-get install git ca-certificates

COPY ./benchmarks/video-processing/init/go.mod ./
COPY ./benchmarks/video-processing/init/go.sum ./
COPY ./benchmarks/video-processing/init/riscv-init-database.go ./init-database.go

RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -v -o ./init-database init-database.go

# Second stage (Runner):
FROM scratch as databaseInit
WORKDIR /app/
COPY --from=databaseInitBuilder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=databaseInitBuilder /app/app/init-database .
COPY ./benchmarks/video-processing/videos/ ./videos

ENTRYPOINT [ "/app/init-database" ]


#---------- PYTHON -----------#
# First stage (Builder):
# Install gRPC and all other dependencies


# FROM vhiveease/python-slim:latest as videoProcessingPythonBuilder
# WORKDIR /py
# COPY ./benchmarks/video-processing/python/requirements.txt ./requirements.txt
# RUN pip3 install --user -r requirements.txt

# Second stage (Runner):
FROM caldiuoa/python-base:debian_grpcio_tools_riscv64  as videoProcessingPython
WORKDIR /app

RUN apt update && apt install -y python3-cassandra python3-opencv
COPY ./benchmarks/video-processing/python/server.py ./
COPY ./benchmarks/video-processing/python/requirements-riscv.txt ./requirements.txt
RUN pip3 install --break-system-packages -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/video-processing/python/riscv-server.py ./server.py
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/video_processing/video_processing_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/video_processing/video_processing_pb2.py ./proto/video_processing/
# COPY --from=videoProcessingPythonBuilder /root/.local /root/.local
# COPY --from=videoProcessingPythonBuilder /py /app
# WORKDIR /app
# # ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python3", "/app/server.py" ]




# python3-opencv python3-cassandra python3-torchvision python3-torch python3-grpc-tools