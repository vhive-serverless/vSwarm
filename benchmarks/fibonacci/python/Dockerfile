## First stage: install all dependencies for this workload
FROM davidschall/python_grpc:base AS builder_workload
COPY --from=davidschall/python_grpc:base /root/.local /root/.local
COPY python/requirements.txt .
RUN pip3 install --user -r requirements.txt


## Second stage: Create the actual image running the workload
## Copy only the important files.
FROM davidschall/python_grpc:base as var_workload
COPY --from=builder_workload /root/.local /root/.local

WORKDIR /app
COPY python/*.py proto/*.py /app/

ENTRYPOINT [ "python", "/app/server.py" ]
