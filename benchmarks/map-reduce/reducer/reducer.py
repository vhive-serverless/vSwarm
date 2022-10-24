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

def ReduceFunction(args : dict):
    log.info(f"Reducer {args['reducerId']} is invoked")

    responses = []
    with tracing.Span("Fetch keys"):
        read_tasks = []
        for key in args['keys']:
            read_tasks.append(key)
        responses = Parallel(backend="threading", n_jobs=len(read_tasks))(
            delayed(args['inputStorage'].get)(i) for i in read_tasks)

    results = {}
    line_count = 0
    start_time = time.time()

    with tracing.Span("Compute reducer result"):
        for resp in responses:
            try:
                for srcIp, val in pickle.loads(resp).items():
                    line_count += 1
                    if srcIp not in results:
                        results[srcIp] = 0
                    results[srcIp] += float(val)
            except:
                log.error(sys.exc_info()[0])

    time_in_secs = time.time() - start_time

    with tracing.Span("Save result"):
        if args['nReducers'] == 1:
            reduceKey = "%sjob_%s/result" % (OUTPUT_REDUCER_PREFIX, args['jobId'])
        else:
            reduceKey = "%sjob_%s/reducer_%d" % (OUTPUT_REDUCER_PREFIX,
                args['jobId'], args['reducerId'])

        metadata = {
            "linecount":  str(line_count),
            "processingtime": str(time_in_secs),
            "memoryUsage": str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        }

        args["outputStorage"].put(reduceKey, pickle.dumps(results), metadata)

    return {
        'reply' : "success"
    }
