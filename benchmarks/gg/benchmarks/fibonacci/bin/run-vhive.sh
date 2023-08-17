#!/bin/bash -e

USAGE="$0 <ADDR> <PORT> <JOBS-COUNT>"

ADDR=${1?$USAGE}
PORT=${2?$USAGE}
JOBS_COUNT=${3?$USAGE}

N="10"

# DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
# cd $DIR/../

cd /app/fibonacci

printf "1. Clear workspace\n"
./bin/clear.sh

printf "2. Initialize gg\n"
gg init

printf "3. Create thunks for number %s\n" "$N"
./create-thunk.sh $N ./fib ./add

printf "4. Run calculation\n"
gg force --jobs=$JOBS_COUNT --engine=vhive=${ADDR}:${PORT} "fib${N}_output"

printf "5. Result: %s\n" $(cat fib${N}_output)
