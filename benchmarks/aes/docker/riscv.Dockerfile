# MIT License
#
# Copyright (c) 2022 David Schall and EASE lab
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

# #---------- PYTHON -----------#
# # First stage (Builder):
# # Install gRPC and all other dependencies


# docker build    --tag caldiuoa/aes-python:riscv64_noble   --target aesPython   -f ./docker/Dockerfile   ../../
# docker push caldiuoa/aes-python:riscv64_noble
FROM --platform=riscv64   caldiuoa/python-base:3.10-grpc-only-1.71 as aesPythonBuilder

WORKDIR /py
COPY ./benchmarks/aes/python/requirements/requirements-riscv.txt ./requirements.txt
RUN pip3 install --user -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/aes/python/server.py ./
# RUN apt-get update && apt-get install -y libc-ares2 libabsl-dev  libprotobuf23 
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/aes/aes_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/aes/aes_pb2.py ./proto/aes/

# # Second stage (Runner):
FROM --platform=riscv64 caldiuoa/python-base:3.10-runner as aesPython
# FROM cartesi/python:3.12-slim-noble  as aesPython
COPY --from=aesPythonBuilder /root/.local /root/.local
COPY --from=aesPythonBuilder /py /app
COPY --from=aesPythonBuilder /usr/lib/riscv64-linux-gnu/libatomic.so* /usr/lib/riscv64-linux-gnu/

WORKDIR /app
ENV PATH=/root/.local/bin:$PATH
ENV LD_PRELOAD /usr/lib/riscv64-linux-gnu/libatomic.so.1
ENTRYPOINT [ "python", "/app/server.py" ]


#---------- GoLang -----------#
# First stage (Builder):
FROM  --platform=riscv64  caldiuoa/go-base:1.21-riscv64 AS aesGoBuilder 
USER root
WORKDIR /app/app/
RUN  apk add git ca-certificates

COPY ./utils/tracing/go ../../utils/tracing/go
COPY ./benchmarks/aes/go/go.mod ./
COPY ./benchmarks/aes/go/go.sum ./
COPY ./benchmarks/aes/go/server.go ./

RUN go mod tidy
RUN CGO_ENABLED=0 GOARCH=riscv64 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o ./server server.go

# Second stage (Runner):
FROM  scratch as aesGo

WORKDIR /app/
COPY --from=aesGoBuilder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=aesGoBuilder /app/app/server .

ENTRYPOINT [ "/app/server" ]


#---------- NodeJS -----------#
# First stage (Builder):
FROM caldiuoa/node-base:jammy-builder AS aesNodeJSBuild
WORKDIR /app/

COPY ./utils/tracing/nodejs ./utils/tracing/nodejs
COPY ./benchmarks/aes/nodejs/package.json ./
RUN npm set progress=false && npm config set depth 0
RUN npm install --only=production

COPY ./benchmarks/aes/nodejs/server.js ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/aes/aes.proto ./

# Second stage (Runner):
FROM caldiuoa/node-base:alpine-runner AS aesNodeJS
WORKDIR /app/
COPY --from=aesNodeJSBuild /app/ .

ENTRYPOINT [ "node", "server.js" ]

EXPOSE 50051



