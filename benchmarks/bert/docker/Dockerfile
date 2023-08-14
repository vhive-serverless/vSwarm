ARG FROM_IMAGE_NAME=nvcr.io/nvidia/tensorflow:19.10-py3
FROM ${FROM_IMAGE_NAME}

RUN apt-get update && apt-get install -y pbzip2 pv bzip2 libcurl4 curl

WORKDIR /workspace

# Install third_party library
RUN mkdir /tmp/third_party \
    && cd /tmp/third_party \
    && git clone https://github.com/pybind/pybind11.git \
    && mv pybind11 pybind \
    && cd /tmp/third_party/pybind \ 
    && git reset --hard 25abf7efba

# Install LoadGen
RUN cd /tmp/ \
    && git clone https://github.com/lrq619/loadgen.git \
    && cd /tmp/loadgen \
    && python3 setup.py install \
    && cd /tmp \
    && rm -rf /tmp/loadgen \
    && rm -rf /tmp/third_party

COPY benchmarks/bert/requirements.txt /workspace/
RUN python3 -m pip install -r requirements.txt

COPY benchmarks/bert/build /workspace/build
COPY benchmarks/bert/python /workspace/python
RUN mv /workspace/python/config/bert_config.json /workspace/ && mv /workspace/python/config/user.conf /workspace/

ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/add-bert/proto/bert/bert_pb2_grpc.py /workspace/python
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/add-bert/proto/bert/bert_pb2.py /workspace/python/proto/bert/

ENTRYPOINT [ "python3", "python/server.py" ,"--addr=0.0.0.0", "--port=50051"]
