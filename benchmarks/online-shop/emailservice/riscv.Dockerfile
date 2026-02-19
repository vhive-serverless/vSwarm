# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

FROM --platform=riscv64   caldiuoa/python-base:3.10-grpc-only-1.71 as builder
WORKDIR /py
# COPY requirements.txt .
COPY riscv-requirements.txt requirements.txt
RUN pip3 install --user -r requirements.txt

COPY . .
RUN rm req* Dockerfile
RUN apt-get update && apt-get install -y libc-ares2 libabsl-dev  libprotobuf23 


FROM --platform=riscv64 caldiuoa/python-base:3.10-runner as release
COPY --from=builder /root/.local /root/.local
COPY --from=builder /py /email_server
COPY --from=builder /usr/lib/riscv64-linux-gnu/libatomic.so* /usr/lib/riscv64-linux-gnu/
# Enable unbuffered logging
ENV PYTHONUNBUFFERED=1
# Enable Profiler
ENV ENABLE_PROFILER=1
WORKDIR /email_server
ENV PATH=/root/.local/bin:$PATH
ENV LD_PRELOAD /usr/lib/riscv64-linux-gnu/libatomic.so.1

EXPOSE 8080
ENTRYPOINT [ "python", "email_server.py" ]
