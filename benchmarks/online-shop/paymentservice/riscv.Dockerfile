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

FROM caldiuoa/node-base:jammy-builder AS base

FROM base as builder

# Some packages (e.g. @google-cloud/profiler) require additional
# deps for post-install scripts
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install grpc-health-check
RUN npm install --only=production

FROM caldiuoa/node-base:alpine-runner AS release




WORKDIR /usr/src/app

COPY --from=builder /usr/src/app/node_modules ./node_modules

COPY . .

EXPOSE 50051
ENV PORT=50051
ENV DISABLE_PROFILER=true
ENV DISABLE_DEBUGGER=true
ENV DISABLE_TRACING=true
ENTRYPOINT [ "node", "index.js" ]
