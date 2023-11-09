#!/bin/bash

# MIT License
#
# Copyright (c) 2023 David Schall and vHive-Serverless
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


PB_VERSION=25.0

PB_REL="https://github.com/protocolbuffers/protobuf/releases"
curl -LO $PB_REL/download/v$PB_VERSION/protoc-$PB_VERSION-linux-x86_64.zip

unzip protoc-$PB_VERSION-linux-x86_64.zip -d $HOME/.local


sh -c  "echo 'export PATH=\$PATH:\$HOME/.local/bin' >> $HOME/.bashrc"
export PATH="$PATH:$HOME/.local/bin"

go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.31
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.3

sh -c  "echo 'export PATH=\$PATH:\$(go env GOPATH)/bin' >> $HOME/.bashrc"
export PATH="$PATH:$(go env GOPATH)/bin"