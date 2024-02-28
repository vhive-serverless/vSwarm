#---------- PYTHON -----------#
# First stage (Builder):
# Install gRPC and all other dependencies
FROM vhiveease/python-slim:latest as parkingPythonBuilder
WORKDIR /py

# copy python requirements
COPY ./benchmarks/spright-parking/python/requirements.txt ./
RUN pip3 install --user -r requirements.txt

# copy related file 
COPY ./benchmarks/spright-parking/python/server.py ./
COPY ./benchmarks/spright-parking/python/hack.py ./

# add proto file from github
# ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/parking/parking_pb2_grpc.py ./
# ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/v0.3.0/proto/parking/parking_pb2.py ./proto/parking_pb2_grpc/
COPY ./benchmarks/spright-parking/python/parking_pb2_grpc.py ./
# COPY ./benchmarks/spright-parking/python/parking_pb2.py ./proto/parking_pb2_grpc/ # prob not working
COPY ./benchmarks/spright-parking/python/parking_pb2.py ./



# Second stage (Runner):
FROM vhiveease/python-slim:latest as parkingPython
COPY --from=parkingPythonBuilder /root/.local /root/.local
COPY --from=parkingPythonBuilder /py /app
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python", "/app/server.py" ]
