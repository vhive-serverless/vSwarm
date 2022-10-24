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

import resource
import sys
import time

from joblib import Parallel, delayed
import logging as log
import pickle

import tracing

INPUT_MAPPER_PREFIX = "artemiy/"
OUTPUT_MAPPER_PREFIX = "artemiy/task/mapper/"
INPUT_REDUCER_PREFIX = OUTPUT_MAPPER_PREFIX
OUTPUT_REDUCER_PREFIX = "artemiy/task/reducer/"

def MapFunction(args : dict):
    log.info(f"Mapper {args['mapperId']} is invoked")

    output = {}
    content_list = []

    start_time = time.time()
    with tracing.Span("Fetch keys"):
        for k in args['keys']:
            key = INPUT_MAPPER_PREFIX + k
            contents = args['inputStorage'].get(key).decode('utf-8')
            content_list.append(contents)

    line_count = 0
    with tracing.Span("process keys and shuffle"):
        for contents in content_list:
            for line in contents.split('\n')[1:-1]:
                line_count +=1
                try:
                    data = line.split(',')
                    srcIp = data[0]
                    if srcIp not in output:
                        output[srcIp] = 0
                    output[srcIp] += float(data[3])
                except Exception as e:
                    log.error(sys.exc_info()[0])

        shuffle_output = []
        for i in range(args['nReducers']):
            shuffle_output.append({})
        for srcIp in output.keys():
            reducer_num = hash(srcIp) & (args['nReducers'] - 1)
            shuffle_output[reducer_num][srcIp] = output[srcIp]

    time_in_secs = time.time() - start_time

    mapReply = None
    if args['mapReply'] is not None:
        mapReply = args['mapReply']()

    with tracing.Span("Save result"):
        write_tasks = []
        for to_reducer_id in range(args['nReducers']):
            mapperKey = "%sjob_%s/shuffle_%d/map_%d" % (OUTPUT_MAPPER_PREFIX,
                args['jobId'], to_reducer_id, args['mapperId'])

            metadata = {
                "linecount":  str(line_count),
                "processingtime": str(time_in_secs),
                "memoryUsage": str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            }
            write_tasks.append((mapperKey,
                pickle.dumps(shuffle_output[to_reducer_id]), metadata))

        keys = Parallel(backend="threading", n_jobs=args['nReducers'])(
            delayed(args['outputStorage'].put)(*i) for i in write_tasks)

    return {'mapReply' : mapReply, 'keys' : keys}
