FROM caldiuoa/debian-base:trixie
# apt install -y python3-torch python3-numpy  python3-pip

# pip install --user --break-system-packages grpcio google protobuf accelerate grpcio-reflection transformers six setuptools pyyaml  --index-url https://gitlab.com/api/v4/projects/56254198/packages/pypi/simple

RUN apt-get update && apt-get install -y pbzip2 pv bzip2 libcurl4 curl build-essential cmake g++ git pkg-config \
    libboost-all-dev libssl-dev \
    libthrift-dev rapidjson-dev \
    ninja-build python3-dev \
    make \
    gcc \
    flex bison \
    libzstd-dev \
    liblz4-dev \
    libsnappy-dev \
    libbrotli-dev \
    libprotobuf-dev protobuf-compiler \
    python3-torch python3-numpy  python3-pip

RUN pip install --user --break-system-packages grpcio google protobuf accelerate grpcio-reflection transformers six setuptools pyyaml  --index-url https://gitlab.com/api/v4/projects/56254198/packages/pypi/simple


RUN mkdir /tmp/third_party \
    && cd /tmp/third_party \
    && git clone https://github.com/pybind/pybind11.git \
    && mv pybind11 pybind \
    && cd /tmp/third_party/pybind  
    # && git reset --hard 25abf7efba

# Install LoadGen
RUN cd /tmp/ \
    && git clone https://github.com/lrq619/loadgen.git \
    && cd /tmp/loadgen \
    && python3 setup.py install \
    && cd /tmp \
    && rm -rf /tmp/loadgen \
    && rm -rf /tmp/third_party

WORKDIR /resources

# FROM caldiuoa/gptj-python:latest_temp


RUN git clone https://github.com/apache/arrow.git
WORKDIR /resources/arrow
RUN git checkout apache-arrow-21.0.0

RUN mkdir /resources/arrow/cpp/build
WORKDIR /resources/arrow/cpp/build

RUN cmake .. \
  -DCMAKE_INSTALL_PREFIX=/usr/local \
  -DARROW_BUILD_SHARED=ON \
  -DARROW_PYTHON=ON \
  -DARROW_PARQUET=ON \
  -DARROW_COMPUTE=ON \
  -DARROW_DATASET=ON \
  -DARROW_IPC=ON \
  -DARROW_CSV=ON \
  -DARROW_JSON=ON \
  -DARROW_WITH_RE2=ON \
  -DARROW_WITH_UTF8PROC=OFF \
  -DARROW_FLIGHT=OFF \
  -DARROW_GANDIVA=OFF \
  -DARROW_HDFS=OFF \
  -DARROW_ORC=OFF \
  -GNinja

RUN ninja -j$(nproc)

RUN ninja install

# ################################################333
WORKDIR /resources/arrow/python

RUN pip install --user  --break-system-packages -r requirements-build.txt cython 

RUN rm -rf build/ pyarrow/*.so

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# RUN python setup.py build_ext --inplace
RUN pip install --user  --break-system-packages -e .


WORKDIR /workspace

COPY ./benchmarks/gptj/python /workspace/python

WORKDIR /workspace/python

RUN cd /tmp/ \
    && git clone https://github.com/vhive-serverless/vSwarm-proto.git \
    && cd /tmp/vSwarm-proto \
    && git checkout feature/gptj \
    && mv /tmp/vSwarm-proto/proto/gptj/* /workspace/python

RUN python3 main_process.py --model-path=EleutherAI/gpt-neo-125M --dataset-path=./data/cnn_eval.json --mlperf_conf=./config/mlperf.conf --user_conf=./config/user.conf  
ENTRYPOINT [ "python3", "server.py",  "--dataset-path=./data/cnn_eval.json", "--mlperf_conf=./config/mlperf.conf", "--user_conf=./config/user.conf"]

# python3 server.py --dataset-path=./data/cnn_eval.json --mlperf_conf=./config/mlperf.conf --user_conf=./config/user.conf