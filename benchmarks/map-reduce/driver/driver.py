# MIT License
#
# Copyright (c) 2021 Michal Baczun and EASE lab
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

import os
import sys

from concurrent import futures
import logging as log

NUM_MAPPERS = int(os.getenv('NUM_MAPPERS', "4"))
NUM_REDUCERS = int(os.getenv('NUM_REDUCERS', "2"))

DEFAULT_BUCKET = "storage-module-test"

def DriveFunction(args: dict):
    log.info("Driver received a request")

    # sanity checks
    if NUM_MAPPERS <= 1 or NUM_REDUCERS <= 0:
        sys.exit("Invalid number of mappers and reducers")
    elif NUM_MAPPERS > 2215:
        sys.exit("Max Number of Mappers allowed is 2215")
    elif NUM_REDUCERS >= NUM_MAPPERS:
        sys.exit("Number of Reducers should be less than the number of mappers")
    elif not ((NUM_REDUCERS & (NUM_REDUCERS - 1) == 0) and NUM_REDUCERS != 0):
        sys.exit("Number of reducers must be a power of 2")

    map_tasks = []
    for i in range(NUM_MAPPERS):
        task = {
            'srcBucket' : DEFAULT_BUCKET,
            'destBucket' : DEFAULT_BUCKET,
            'keys'      : ["part-" + str(i).zfill(5)],
            'jobId'     : "0",
            'mapperId'  : i,
            'nReducers' : NUM_REDUCERS
        }
        map_tasks.append(task)

    mapper_responses = []
    ex = futures.ThreadPoolExecutor(max_workers=NUM_MAPPERS)
    all_result_futures = ex.map(args['callMapperMethod'], map_tasks)

    reduce_input_keys = args['prepareReduceKeys'](all_result_futures, NUM_REDUCERS)

    log.info("calling mappers done")

    reduce_tasks = []
    for i in range(NUM_REDUCERS):
        task = {
            'srcBucket' : DEFAULT_BUCKET,
            'destBucket' : DEFAULT_BUCKET,
            'keys'      : reduce_input_keys[i],
            'nReducers' : NUM_REDUCERS,
            'jobId'     : "0",
            'reducerId' : i
        }
        reduce_tasks.append(task)

    reducer_responses = []
    ex = futures.ThreadPoolExecutor(max_workers=NUM_REDUCERS)
    ex.map(args['callReducerMethod'], reduce_tasks)

    log.info("calling reducers done")
