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
# First stage (Builder):
# Install gRPC and all other dependencies
FROM vhiveease/python-slim:latest as aesPythonBuilder
WORKDIR /py
COPY ./benchmarks/aes/python/requirements.txt ./
RUN pip3 install --user -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/aes/python/server.py ./
COPY ./benchmarks/aes/proto/helloworld_pb2_grpc.py ./
COPY ./benchmarks/aes/proto/helloworld_pb2.py ./

# Second stage (Runner):
FROM vhiveease/python-slim:latest as aesPython
COPY --from=aesPythonBuilder /root/.local /root/.local
COPY --from=aesPythonBuilder /py /app
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]




#---------- GoLang -----------#
# First stage (Builder):
FROM golang:1.16-alpine AS aesGoBuilder
WORKDIR /app/app/
RUN apk add --no-cache make git
RUN apk add -U --no-cache ca-certificates

COPY ./utils/tracing/go ../../utils/tracing/go
COPY ./benchmarks/aes/go.mod ./
COPY ./benchmarks/aes/go.sum ./
COPY ./benchmarks/aes/proto ./proto
COPY ./benchmarks/aes/go/server.go ./

RUN go mod download && \
    CGO_ENABLED=0 GOOS=linux go build -v -o ./server server.go


# Second stage (Runner):
FROM scratch as aesGo
WORKDIR /app/
COPY --from=aesGoBuilder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=aesGoBuilder /app/app/server .

ENTRYPOINT [ "/app/server" ]




#---------- NodeJS -----------#
# First stage (Builder):
FROM node:stretch-slim AS aesNodeJSBuild
WORKDIR /app/

COPY ./utils/tracing/nodejs ./utils/tracing/nodejs
COPY ./benchmarks/aes/nodejs/package.json ./
COPY ./benchmarks/aes/nodejs/server.js ./
COPY ./benchmarks/aes/proto/helloworld.proto ./

RUN npm set progress=false && npm config set depth 0
RUN npm install --only=production

# Second stage (Runner):
FROM node:stretch-slim AS aesNodeJS
WORKDIR /app/
COPY --from=aesNodeJSBuild /app/ .

ENTRYPOINT [ "node", "server.js" ]

