#!/usr/bin/env bash
START=$1
END=$2
STEP=$3
DUR=$4
CMD=$5

if [ -z "$DUR" ]; then
    DUR=10
fi
echo duration=$DUR

if [ "$CMD" != "coldstart" ] && [ "$CMD" != "run" ]; then
    echo Wrong cmd: $CMD
    exit 1
else
    echo CMD=$CMD
fi

for i in $( seq $START $STEP $END ); do
    echo "make ARGS=--rps $i --duration $DUR $CMD"
    make ARGS="--rps $i --duration $DUR" $CMD
done