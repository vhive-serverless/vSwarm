FROM debian:trixie-20250908-slim AS python-debian-base-with-grpcio-tools

RUN apt-get update && apt-get install -y python3-dev python3-pip

RUN pip install --user --break-system-packages grpcio grpcio-tools --index-url https://gitlab.com/api/v4/projects/56254198/packages/pypi/simple

#######################################
FROM debian:trixie-20250908-slim AS debian-trixie
# pourpourr/debian-base:trixie

#######################################

FROM debian:trixie-20250908-slim AS python-debian-base-grpc-only

RUN apt-get update && apt-get install -y python3-dev python3-pip

RUN pip install --user --break-system-packages grpcio  --index-url https://gitlab.com/api/v4/projects/56254198/packages/pypi/simple

# pourpourr/python-base:debian_grpc_only_riscv64 

#######################################

FROM riscv64/python:3.11-trixie AS python3.11-trixie
# pourpourr/python-base:3.11-trixie

#######################################

FROM riscv64/python:3.11-slim-trixie AS python3.11-trixie-runner
#grpc 1.72 gprc  grpcio_tools-1.71.2 protobuf-5.29.5 setuptools-80

# pourpourr/python-base:3.11-trixie-runner

#######################################

FROM python:3.13.6-slim-trixie AS python-debian-slim-runner


#######################################

FROM  golang:1.21-alpine AS go-alpine-base
# pourpourr/go-base:1.21-riscv64 

#######################################

FROM  cartesi/node:18-jammy AS node-jammy-base
# pourpourr/node-base:jammy-builder

#######################################

FROM natheesan/node:18.16.1-alpine AS node-alpine-runner
# pourpourr/node-base:alpine-runner

#######################################

FROM riscv64/eclipse-temurin:17-jdk-noble AS java-17-builder
#  pourpourr/java-builder:17 
#######################################

FROM riscv64/eclipse-temurin:17-jre-noble AS java-17-runner
# pourpourr/java-runner:17
#######################################

FROM ubuntu:noble AS noble-base
# pourpourr/noble-base:latest
#######################################

FROM redis:alpine AS  redis

#######################################

FROM --platform=riscv64 cartesi/python:3.10-slim-jammy AS python3.10-runner
# pourpourr/python-base:3.10-runner

#######################################

FROM --platform=riscv64   cartesi/python:3.10-jammy AS python3.10-grpc-only-1.71
RUN pip3 install --user grpcio==1.71.0

# pourpourr/python-base:3.10-grpc-only-1.71
#######################################

FROM python3.10-grpc-only-1.71 AS python3.10-grpc-grpc-tools-1.71
RUN pip3 install --user grpcio-tools==1.71.0

# FROM --platform=riscv64   cartesi/python:3.10-jammy as python-jammy-grpc
# RUN pip3 install --user grpcio==1.71.0


# FROM  python-jammy-grpc AS python-jammy-grpc-tools