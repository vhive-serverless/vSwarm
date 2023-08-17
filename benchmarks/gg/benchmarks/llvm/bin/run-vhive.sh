#!/bin/bash
# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# cd $DIR/../

cd /app/llvm

USAGE="$0 <ADDR> <PORT> <JOBS-COUNT>"

ADDR=${1?$USAGE}
PORT=${2?$USAGE}
JOBS_COUNT=${3?$USAGE}

apt-get update
apt-get -y install cmake

# if [ ! -d "llvm-project" ]; then
#   printf "0. Clone LLVM from Github (it may take some time)\n"

#   git clone https://github.com/llvm/llvm-project
# fi
tar -xzvf llvm.tar.gz

printf "1. Clear workspace\n"
./bin/clear.sh

printf "2. Create build dir (llvm-build)\n"
mkdir llvm-build
cd llvm-build

printf "3. Initialize gg\n"
gg init

printf "4. Build llvm using patched cmake (see gg/src/models/wrappers/cmake)\n"
gg infer cmake ../llvm-project/llvm

printf "5. Create thunks for building llvm-tblgen\n"
gg infer make -j`nproc` llvm-tblgen

printf "6. Input trunk:\n"
cat bin/llvm-tblgen

printf "7. Build llvm-tblgen\n"
gg force --jobs=$JOBS_COUNT --engine=vhive=${ADDR}:${PORT} bin/llvm-tblgen
