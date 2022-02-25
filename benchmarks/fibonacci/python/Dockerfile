## First stage:
## Install gRPC and all other dependencies
FROM python:3.8-slim AS builder

## gRPC
ENV GRPC_PYTHON_VERSION 1.44.0
ENV PROTOBUF_VERSION 3.11.3
RUN pip3 install --user grpcio==${GRPC_PYTHON_VERSION} grpcio-tools==${GRPC_PYTHON_VERSION}


## Workload dependent libraries
COPY requirements.txt .
RUN pip3 install --user -r requirements.txt


## Second stage: Create the actual image running the workload
## Copy only the installation files.
FROM python:3.8-slim as var_workload
COPY --from=builder /root/.local /root/.local

WORKDIR /app
COPY *.py /app/

ENTRYPOINT [ "python", "/app/server.py" ]
