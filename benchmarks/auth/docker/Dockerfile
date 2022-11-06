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
FROM vhiveease/python-slim:latest as authPythonBuilder
WORKDIR /py
COPY ./benchmarks/auth/python/requirements/common.txt ./requirements.txt
RUN pip3 install --user -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/auth/python/server.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/auth/auth_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/auth/auth_pb2.py ./proto/auth/

# Second stage (Runner):
FROM vhiveease/python-slim:latest as authPython
COPY --from=authPythonBuilder /root/.local /root/.local
COPY --from=authPythonBuilder /py /app
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]




#---------- GoLang -----------#
## First stage (Builder):
FROM vhiveease/golang-builder:latest AS authGoBuilder
WORKDIR /app/app/
RUN apt-get install git ca-certificates

COPY ./utils/tracing/go ../../utils/tracing/go
COPY ./benchmarks/auth/go/go.mod ./
COPY ./benchmarks/auth/go/go.sum ./
COPY ./benchmarks/auth/go/server.go ./

RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -v -o ./server server.go

# Second stage (Runner):
FROM scratch as authGo
WORKDIR /app/
COPY --from=authGoBuilder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=authGoBuilder /app/app/server .

ENTRYPOINT [ "/app/server" ]




#---------- NodeJS -----------#
# First stage (Builder):
FROM vhiveease/node-slim:latest AS authNodeJSBuild
WORKDIR /app/

COPY ./utils/tracing/nodejs ./utils/tracing/nodejs
COPY ./benchmarks/auth/nodejs/package.json ./
COPY ./benchmarks/auth/nodejs/server.js ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/auth/auth.proto ./

RUN npm set progress=false && npm config set depth 0
RUN npm install --only=production

# Second stage (Runner):
FROM node:stretch-slim AS authNodeJS
WORKDIR /app/
COPY --from=authNodeJSBuild /app/ .

ENTRYPOINT [ "node", "server.js" ]
