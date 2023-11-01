# Use an official Python runtime as the base image
FROM python:3.10-slim

RUN apt-get update && apt-get install -y pbzip2 pv bzip2 libcurl4 curl python3.10 git  build-essential

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

COPY benchmarks/gptj/python /workspace/python

RUN cd /tmp/ \
    && git clone https://github.com/vhive-serverless/vSwarm-proto.git \
    && cd /tmp/vSwarm-proto \
    && git checkout feature/gptj \
    && mv /tmp/vSwarm-proto/proto/gptj/* /workspace/python

RUN pip install pip==23.3
RUN cd /workspace/python && pip3 install -r /workspace/python/requirements.txt

EXPOSE 50051

ENTRYPOINT [ "python3", "python/server.py",  "--dataset-path=python/data/cnn_eval.json", "--mlperf_conf=python/config/mlperf.conf", "--user_conf=python/config/user.conf"]
