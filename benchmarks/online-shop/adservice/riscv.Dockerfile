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

FROM caldiuoa/java-builder:17  as builder
WORKDIR /app

# COPY ["build-riscv.gradle", "gradlew", "./"]
# COPY riscv-gradle gradle
RUN apt  update && apt-get install -y  protobuf-compiler-grpc-java-plugin protobuf-compiler
COPY . . 
RUN rm -rf build.gradle  Dockerfile .gitignore gradle/ riscv.Dockerfile
RUN mv riscv-gradle gradle
RUN mv build-riscv.gradle build.gradle
RUN chmod +x gradlew
# RUN curl -L -o google-java-format.jar https://github.com/google/google-java-format/releases/download/v1.22.0/google-java-format-1.22.0-all-deps.jar 
# RUN  alias google-java-format='java -jar ./google-java-format.jar'
# RUN google-java-format -i /app/src/main/java/hipstershop/AdService.java
RUN ./gradlew downloadRepos
RUN ./gradlew installDist


FROM caldiuoa/java-runner:17

RUN GRPC_HEALTH_PROBE_VERSION=v0.4.39 && \
    if [ $(uname -i) == "riscv64" ]; then ARCH=riscv64 ; else ARCH=amd64; fi && \
    wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-${ARCH} && \
    chmod +x /bin/grpc_health_probe
WORKDIR /app
COPY --from=builder /app .


# FROM caldiuoa/onlineshop-adservice:riscv64GradleFinal5
EXPOSE 9555

ENV PORT=9555
ENV DISABLE_PROFILER=true
ENV DISABLE_DEBUGGER=true
ENV DISABLE_TRACING=true
ENV DISABLE_STATS=true

ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]



# RUN apt update && apt install nano 
# WORKDIR /app

# RUN ./gradlew downloadRepos
# RUN chmod +x gradlew


# FROM caldiuoa/onlineshop-adservice:riscv64GradleFinal3 as builder
# COPY . .
# RUN chmod +x gradlew

# RUN apt-get -y update && apt-get install -qqy \
#     wget \
#     && rm -rf /var/lib/apt/lists/*



# FROM riscv64/eclipse-temurin:17-jdk-noble

# Download Stackdriver Profiler Java agent
# RUN apt-get -y update && apt-get install -qqy \
#     wget \
#     && rm -rf /var/lib/apt/lists/*
# RUN mkdir -p /opt/cprof && \
#     wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent.tar.gz \
#     | tar xzv -C /opt/cprof && \
#     rm -rf profiler_java_agent.tar.gz

# RUN GRPC_HEALTH_PROBE_VERSION=v0.4.11 && \
#     if [ $(uname -i) == "aarch64" ]; then ARCH=arm64 ; else ARCH=amd64; fi && \
#     wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-${ARCH} && \
#     chmod +x /bin/grpc_health_probe
# RUN GRPC_HEALTH_PROBE_VERSION=v0.4.39 && \
#     if [ $(uname -i) == "riscv64" ]; then ARCH=riscv64 ; else ARCH=amd64; fi && \
#     wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-${ARCH} && \
#     chmod +x /bin/grpc_health_probe
# WORKDIR /app
# COPY --from=builder /app .


# FROM caldiuoa/onlineshop-adservice:riscv64GradleFinal5
# EXPOSE 9555
# ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]





# RUN chmod +x gradlew
# RUN ./gradlew installDist

# FROM openjdk:8-slim

# # Download Stackdriver Profiler Java agent
# RUN apt-get -y update && apt-get install -qqy \
#     wget \
#     && rm -rf /var/lib/apt/lists/*
# RUN mkdir -p /opt/cprof && \
#     wget -q -O- https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent.tar.gz \
#     | tar xzv -C /opt/cprof && \
#     rm -rf profiler_java_agent.tar.gz

# RUN GRPC_HEALTH_PROBE_VERSION=v0.4.11 && \
#     if [ $(uname -i) == "aarch64" ]; then ARCH=arm64 ; else ARCH=amd64; fi && \
#     wget -qO/bin/grpc_health_probe https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/${GRPC_HEALTH_PROBE_VERSION}/grpc_health_probe-linux-${ARCH} && \
#     chmod +x /bin/grpc_health_probe

# WORKDIR /app
# COPY --from=builder /app .

# EXPOSE 9555
# ENTRYPOINT ["/app/build/install/hipstershop/bin/AdService"]
