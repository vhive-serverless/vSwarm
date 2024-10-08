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
FROM vhiveease/golang-builder:latest AS databaseInitBuilder
WORKDIR /app/app/
RUN apt-get install git ca-certificates

COPY ./benchmarks/video-processing/init/go.mod ./
COPY ./benchmarks/video-processing/init/go.sum ./
COPY ./benchmarks/video-processing/init/init-database.go ./

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
FROM vhiveease/python-slim:latest as videoProcessingPythonBuilder
WORKDIR /py
COPY ./benchmarks/video-processing/python/requirements.txt ./requirements.txt
RUN pip3 install --user -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/video-processing/python/server.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/video_processing/video_processing_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/video_processing/video_processing_pb2.py ./proto/video_processing/

# Second stage (Runner):
FROM vhiveease/python-slim:latest as videoProcessingPython
COPY --from=videoProcessingPythonBuilder /root/.local /root/.local
COPY --from=videoProcessingPythonBuilder /py /app
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python3", "/app/server.py" ]
