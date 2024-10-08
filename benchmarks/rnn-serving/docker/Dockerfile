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
FROM vhiveease/python-slim:latest as rnnServingPythonBuilder
WORKDIR /py
COPY ./benchmarks/rnn-serving/python/requirements.txt ./requirements.txt
RUN pip3 install --user -r requirements.txt
COPY ./utils/tracing/python/tracing.py ./
COPY ./benchmarks/rnn-serving/python/server.py ./
COPY ./benchmarks/rnn-serving/python/rnn.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/rnn_serving/rnn_serving_pb2_grpc.py ./
ADD https://raw.githubusercontent.com/vhive-serverless/vSwarm-proto/main/proto/rnn_serving/rnn_serving_pb2.py ./proto/rnn_serving/

# Second stage (Runner):
FROM vhiveease/python-slim:latest as rnnServingPython
COPY --from=rnnServingPythonBuilder /root/.local /root/.local
COPY --from=rnnServingPythonBuilder /py /app
COPY ./benchmarks/rnn-serving/model/ /app/model
WORKDIR /app
# ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT [ "python3", "/app/server.py" ]
