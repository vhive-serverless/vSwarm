## First stage:
## Install gRPC and all other dependencies
FROM python:3.8-slim AS builder

## Workload dependent libraries
COPY ./benchmarks/aes/python/requirements.txt .
RUN pip3 install --user -r requirements.txt

## Second stage: Create the actual image running the workload
## Copy only the installation files.
FROM python:3.8-slim as var_workload
COPY --from=builder /root/.local /root/.local

WORKDIR /app
COPY ./utils/tracing/python/tracing.py /app/
COPY ./benchmarks/aes/python/* /app/

ENTRYPOINT [ "python", "/app/server.py" ]
