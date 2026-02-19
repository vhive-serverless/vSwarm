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
    
#---------- PYTHON -----------#
# First stage (Builder):
# Install gRPC and all other dependencies


FROM caldiuoa/python-base:3.11-trixie as rnnServingPythonBuilder
WORKDIR /py

WORKDIR /py/resources/

RUN git clone https://github.com/zhangwm-pt/prebuilt_whl.git 

WORKDIR /py/resources/prebuilt_whl

RUN pip install --user   ./protobuf-4.23.3-py3-none-any.whl ./numpy-1.25.0-cp311-cp311-linux_riscv64.whl  ./networkx-3.1-py3-none-any.whl  ./mpmath-1.3.0-py3-none-any.whl  ./sympy-1.12-py3-none-any.whl  ./typing_extensions-4.7.0-py3-none-any.whl  ./Pillow-9.5.0-cp311-cp311-linux_riscv64.whl  ./MarkupSafe-2.1.3-cp311-cp311-linux_riscv64.whl  ./Jinja2-3.1.2-py3-none-any.whl  ./torch-2.0.0a0+gitc263bd4-cp311-cp311-linux_riscv64.whl
COPY ./benchmarks/rnn-serving/python/riscv-requirements.txt ./requirements.txt
RUN pip3 install --user -r requirements.txt
WORKDIR /py
COPY ./benchmarks/rnn-serving/python/riscv-server.py ./server.py
COPY ./benchmarks/rnn-serving/python/rnn.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/rnn_serving/rnn_serving_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/rnn_serving/rnn_serving_pb2.py ./proto/rnn_serving/
RUN rm -r  /py/resources/

FROM caldiuoa/python-base:3.11-trixie-runner as rnnServingPython
WORKDIR /app
COPY --from=rnnServingPythonBuilder /usr/lib/riscv64-linux-gnu/libatomic.so* /usr/lib/riscv64-linux-gnu/
COPY --from=rnnServingPythonBuilder /usr/lib/riscv64-linux-gnu/libgomp.so* /usr/lib/riscv64-linux-gnu/
COPY --from=rnnServingPythonBuilder /root/.local /root/.local
COPY --from=rnnServingPythonBuilder /py /app
COPY ./benchmarks/rnn-serving/model/ /app/model
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python3", "/app/server.py" ]



