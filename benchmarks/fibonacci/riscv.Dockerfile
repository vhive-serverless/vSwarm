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

# First stage (Builder):

# FROM caldiuoa/python-base:grpc_grpc-tools-1.66.0  as fibonacciPythonBuilder

# docker build    --tag caldiuoa/fibonacci-python:riscv64_noble   --target fibonacciPython   -f ./Dockerfile   ../../
# FROM caldiuoa/python-riscv64-alpine-base:grpc_grpc-tools-1.71.0 as fibonacciPythonBuilder
FROM --platform=riscv64   caldiuoa/python-base:3.10-grpc-only-1.71 as fibonacciPythonBuilder
WORKDIR /py
COPY ./benchmarks/fibonacci/python/requirements-riscv.txt requirements.txt
RUN pip3 install --user -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/fibonacci/python/server.py ./
# RUN apt install python3-grpcio python3-grpc-tools -y
# RUN apt-get update && apt-get install -y libc-ares2 libabsl-dev  libprotobuf32t64  python3-grpcio python3-grpc-tools -y
#  libprotobuf23 
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci_pb2.py ./proto/fibonacci/

# Second stage (Runner):
FROM --platform=riscv64 caldiuoa/python-base:3.10-runner as fibonacciPython
COPY --from=fibonacciPythonBuilder /root/.local /root/.local
COPY --from=fibonacciPythonBuilder /py /app
COPY --from=fibonacciPythonBuilder /usr/lib/riscv64-linux-gnu/libatomic.so* /usr/lib/riscv64-linux-gnu/

# COPY --from=fibonacciPythonBuilder /usr/lib/libstdc++.so* /usr/lib/
# COPY --from=fibonacciPythonBuilder /usr/lib/libgcc_s.so* /usr/lib/

# RUN apt-get update && apt-get install -y libc-ares2 libabsl-dev  libprotobuf32t64  python3-grpcio python3-grpc-tools -y

WORKDIR /app
# RUN apk add libstdc++
ENV LD_PRELOAD /usr/lib/riscv64-linux-gnu/libatomic.so.1
# ENV /usr/lib/python3/dist-packages/
ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]



###############GO


FROM  --platform=riscv64  caldiuoa/go-base:1.21-riscv64  AS fibonacciGoBuilder
USER root
WORKDIR /app/app/
RUN  apk add git ca-certificates
COPY ./utils/tracing/go ../../utils/tracing/go
COPY ./benchmarks/fibonacci/go.mod ./
COPY ./benchmarks/fibonacci/go.sum ./
COPY ./benchmarks/fibonacci/go/server.go ./
RUN go mod tidy
RUN CGO_ENABLED=0 GOARCH=riscv64 GOOS=linux go build -a -ldflags '-extldflags "-static"' -o ./server server.go

FROM scratch AS fibonacciGo

WORKDIR /app/

COPY --from=fibonacciGoBuilder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=fibonacciGoBuilder /app/app/server .
# USER root:root

ENTRYPOINT [ "/app/server" ]

############NODEJS

FROM caldiuoa/node-base:jammy-builder AS fibonacciNodeJSBuild
WORKDIR /app/

COPY ./utils/tracing/nodejs ./utils/tracing/nodejs
COPY ./benchmarks/fibonacci/nodejs/ ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/fibonacci/fibonacci.proto ./

RUN npm set progress=false && npm config set depth 0
RUN npm install --only=production

# Second stage (Runner):
FROM caldiuoa/node-base:alpine-runner AS fibonacciNodeJS
WORKDIR /app/
COPY --from=fibonacciNodeJSBuild /app/ .

ENTRYPOINT [ "node", "server.js" ]
