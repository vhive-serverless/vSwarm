# MIT License
#
# Copyright (c) 2021 Michal Baczun and EASE lab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

FROM python:3.8-slim-buster as server
WORKDIR /app
COPY ./utils/tracing/integ-tests/client-server/requirements.txt .
COPY ./utils/tracing/integ-tests/client-server/*.py ./
COPY ./utils/tracing/python/tracing.py .
RUN pip3 install --user -r requirements.txt

EXPOSE 50051

STOPSIGNAL SIGKILL

ENTRYPOINT ["python3", "-u", "./server.py"]

FROM python:3.8-slim-buster as client
WORKDIR /app
COPY ./utils/tracing/integ-tests/client-server/requirements.txt .
COPY ./utils/tracing/integ-tests/client-server/*.py ./
COPY ./utils/tracing/python/tracing.py .
RUN pip3 install --user -r requirements.txt

EXPOSE 50051

STOPSIGNAL SIGKILL

ENTRYPOINT ["python3", "-u", "./greeter_client.py"]

