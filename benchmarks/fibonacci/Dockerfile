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


#---------- PYTHON -----------#
## First stage (Builder):
## Install gRPC and all other dependencies
FROM vhiveease/python-slim:latest as fibonacciPythonBuilder
WORKDIR /py
COPY ./benchmarks/fibonacci/python/requirements.txt ./
RUN pip3 install --user -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/fibonacci/python/server.py ./
COPY ./benchmarks/fibonacci/proto/helloworld_pb2_grpc.py ./
COPY ./benchmarks/fibonacci/proto/helloworld_pb2.py ./

# Second stage (Runner):
FROM vhiveease/python-slim:latest as fibonacciPython
COPY --from=fibonacciPythonBuilder /root/.local /root/.local
COPY --from=fibonacciPythonBuilder /py /app
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]




#---------- GoLang -----------#
## First stage (Builder):
FROM vhiveease/golang-builder:latest AS fibonacciGoBuilder
WORKDIR /app/app/
RUN apk add --no-cache make git
RUN apk add -U --no-cache ca-certificates

COPY ./utils/tracing/go ../../utils/tracing/go
COPY ./benchmarks/fibonacci/go.mod ./
COPY ./benchmarks/fibonacci/go.sum ./
COPY ./benchmarks/fibonacci/proto ./proto
COPY ./benchmarks/fibonacci/go/server.go ./

RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -v -o ./server server.go

# Second stage (Runner):
FROM scratch as fibonacciGo
WORKDIR /app/
COPY --from=fibonacciGoBuilder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=fibonacciGoBuilder /app/app/server .

ENTRYPOINT [ "/app/server" ]




#---------- NodeJS -----------#
# First stage (Builder):
FROM node-slim:latest AS fibonacciNodeJSBuild
WORKDIR /app/

COPY ./utils/tracing/nodejs ./utils/tracing/nodejs
COPY ./benchmarks/fibonacci/nodejs/package.json ./
COPY ./benchmarks/fibonacci/nodejs/server.js ./
COPY ./benchmarks/fibonacci/proto/helloworld.proto ./

RUN npm set progress=false && npm config set depth 0
RUN npm install --only=production

# Second stage (Runner):
FROM node-slim:latest AS fibonacciNodeJS
WORKDIR /app/
COPY --from=fibonacciNodeJSBuild /app/ .

ENTRYPOINT [ "node", "server.js" ]


#---------- CPP -----------#
# First stage (Builder):
FROM gcc:10 AS fibonacciCPPBuild
WORKDIR /app/

COPY ./benchmarks/fibonacci/cpp/* ./
COPY ./benchmarks/fibonacci/proto/* ./proto/

RUN apt update && apt install -y protobuf-compiler protobuf-compiler-grpc libgrpc++-dev
RUN ls -lR
RUN mkdir gen && \
    protoc --proto_path=/app/proto --cpp_out=gen helloworld.proto && \
    protoc --proto_path=/app/proto --grpc_out=gen --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` helloworld.proto
RUN g++ -O3 -flto main.cpp gen/helloworld.grpc.pb.cc gen/helloworld.pb.cc -Igen -lgrpc++ -lprotobuf -lgrpc

FROM gcc:10 AS fibonacciCPP
WORKDIR /app/
COPY --from=fibonacciCPPBuild /app/ .

ENTRYPOINT ["/app/a.out"]
