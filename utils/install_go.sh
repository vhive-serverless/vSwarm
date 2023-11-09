#!/bin/bash

# MIT License
#
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

set -e

VERSION=1.21.4
ARCH=amd64

if [ $(uname -i) == "aarch64" ]; then ARCH=arm64 ; fi

GO_BUILD="go${VERSION}.linux-${ARCH}"

wget --continue https://golang.org/dl/${GO_BUILD}.tar.gz

sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf ${GO_BUILD}.tar.gz

export PATH=$PATH:/usr/local/go/bin

sudo sh -c  "echo 'export PATH=\$PATH:/usr/local/go/bin' >> /etc/profile"
sh -c  "echo 'export PATH=\$PATH:/usr/local/go/bin' >> $HOME/.bashrc"

echo "Installed: $(go version)"