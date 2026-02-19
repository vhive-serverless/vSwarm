
  # Copyright 2021 Google LLC
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

FROM caldiuoa/noble-base:latest as builder
RUN apt-get update && apt-get install -y wget nano git cmake g++ make autoconf libtool pkg-config build-essential protobuf-compiler

WORKDIR /grpcPlugin

RUN git clone -b v1.61.0 https://github.com/grpc/grpc && \
    cd grpc && \
    git submodule update --init --recursive && \
    mkdir -p cmake/build && \
    cd cmake/build && \
    cmake ../.. -DgRPC_BUILD_CSHARP_PLUGIN=ON -DgRPC_BUILD_TESTS=OFF && \
    make grpc_csharp_plugin -j$(nproc)


RUN cp grpc/cmake/build/grpc_csharp_plugin /usr/local/bin/ && \
    chmod +x /usr/local/bin/grpc_csharp_plugin    

ENV  PROTOBUF_PLUGIN=/usr/local/bin/grpc_csharp_plugin
ENV  PROTOBUF_PROTOC=/usr/bin/protoc  

WORKDIR /dotnetFiles

RUN wget https://github.com/dkurt/dotnet_riscv/releases/download/v9.0.100/dotnet-sdk-9.0.100-linux-riscv64-gcc-ubuntu-24.04.tar.gz
RUN tar -xvzf dotnet-sdk-9.0.100-linux-riscv64-gcc-ubuntu-24.04.tar.gz 

RUN chmod +x dotnet
RUN cp -r . /usr/local/bin
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
ENV DOTNET_ROOT=/usr/local/bin
ENV PATH=$DOTNET_ROOT:$PATH

WORKDIR /app

COPY . .
RUN mv riscv-cartservice.csproj cartservice.csproj
RUN rm riscv.Dockerfile 
RUN dotnet restore cartservice.csproj || true

RUN mkdir -p /root/.nuget/packages/grpc.tools/2.71.0/tools/linux_/ 
RUN ln -sf /usr/local/bin/grpc_csharp_plugin /root/.nuget/packages/grpc.tools/2.71.0/tools/linux_/grpc_csharp_plugin
RUN chmod +x /root/.nuget/packages/grpc.tools/2.71.0/tools/linux_/grpc_csharp_plugin

RUN dotnet publish cartservice.csproj \
  -p:PublishSingleFile=true \
  -p:UseAppHost=true \
  -r linux-riscv64 \
  --self-contained false \
  -c Release \
  -o /cartservice




FROM caldiuoa/noble-base:latest

# Only needed for globalization (if your app uses it)
RUN apt-get update && apt-get install -y libicu-dev && rm -rf /var/lib/apt/lists/*


ENV DOTNET_ROOT=/usr/local/dotnet
ENV PATH=$DOTNET_ROOT:$PATH
ENV DOTNET_EnableDiagnostics=0
ENV ASPNETCORE_URLS=http://*:7070

# Copy ONLY the necessary .NET runtime from builder stage
COPY --from=builder /dotnetFiles/dotnet /usr/local/dotnet/dotnet
COPY --from=builder /dotnetFiles/shared /usr/local/dotnet/shared
COPY --from=builder /dotnetFiles/host /usr/local/dotnet/host

# Copy your app
WORKDIR /cartservice
COPY --from=builder /cartservice .
ENV DISABLE_PROFILER=true
ENV DISABLE_DEBUGGER=true
ENV DISABLE_TRACING=true
ENV REDIS_ADDR=redis:6379
# Make sure your app binary is executable
# RUN chmod +x /cartservice/cartservice

ENTRYPOINT ["/cartservice/cartservice"]





























# FROM ubuntu:noble 
# WORKDIR /dotnetFiles
# RUN apt-get update && apt-get install -y wget nano
# # WORKDIR /app
# RUN wget https://github.com/dkurt/dotnet_riscv/releases/download/v9.0.100/dotnet-sdk-9.0.100-linux-riscv64-gcc-ubuntu-24.04.tar.gz
# RUN tar -xvzf dotnet-sdk-9.0.100-linux-riscv64-gcc-ubuntu-24.04.tar.gz 
# RUN chmod +x dotnet
# RUN cp -r . /usr/local/bin
# WORKDIR /cartservice
# COPY --from=builder /cartservice .
# ENV ASPNETCORE_URLS http://*:7070
# ENV DOTNET_ROOT=/usr/local/bin
# ENV PATH=$DOTNET_ROOT:$PATH
# ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=0
# RUN apt install -y  libicu-dev


# ENTRYPOINT ["/cartservice/cartservice"]







# ENV ASPNETCORE_URLS http://*:7070
# ENV DOTNET_ROOT=/usr/local/bin
# ENV PATH=$DOTNET_ROOT:$PATH
# ENTRYPOINT ["/cartservice/cartservice"]