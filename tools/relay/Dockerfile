# MIT License

# Copyright (c) 2022 EASE lab

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

# First stage (Builder):
FROM vhiveease/golang-builder:latest AS relayBuilder
WORKDIR /app/app/
RUN apt-get install git ca-certificates

COPY ./tools/relay/ ./tools/relay/
COPY ./utils/tracing/go/ ./utils/tracing/go/

WORKDIR /app/app/tools/relay
RUN go mod tidy
RUN CGO_ENABLED=0 GOOS=linux go build -v -o ./server github.com/vhive-serverless/vSwarm/tools/relay

# Second stage (Runner):
FROM scratch as relay
WORKDIR /app/
COPY --from=relayBuilder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=relayBuilder /app/app/tools/relay/server .

ENTRYPOINT [ "/app/server" ]