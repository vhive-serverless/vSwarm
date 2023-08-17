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

import logging as log

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']
TRANSFER = os.environ.get('TRANSFER_TYPE', 'S3')

supportedTransfers = ['S3', 'ELASTICACHE', 'XDT']
if TRANSFER not in supportedTransfers:
    errmsg = "Error in Environment Variable TRANSFER_TYPE: "
    errmsg += "TRANSFER_TYPE should contain one of " + str(supportedTransfers)
    sys.exit(errmsg)

if TRANSFER == 'S3':
    import boto3

if TRANSFER == 'ELASTICACHE':
    import redis

if TRANSFER == 'XDT':
    import destination as XDTdst
    import source as XDTsrc
    import utils as XDTutil


class Storage:
    def __init__(self, bucket, transferConfig=None):
        self.bucket = bucket
        if TRANSFER == 'S3':
            if LAMBDA:
                self.s3Bucket = boto3.resource(service_name='s3').Bucket(bucket)
            else:
                self.s3Bucket = boto3.resource(
                    service_name='s3',
                    region_name=os.environ.get('AWS_REGION'),
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
                ).Bucket(bucket)
        elif TRANSFER == 'ELASTICACHE':
            host, port = bucket.split(":")
            self.elasticache_client = redis.Redis(host=host, port=port)
        elif TRANSFER == 'XDT':
            if transferConfig is None:
                log.fatal("Transfer Config cannot be empty for XDT transfers")
            self.XDTconfig = transferConfig
            self.XDTclient = XDTsrc.XDTclient(config=self.XDTconfig)

    def put(self, key, obj, metadata=None):
        log.info("Uploading Object with key '" + key + "' to " + TRANSFER)

        if TRANSFER == 'S3':
            s3obj = self.s3Bucket.Object(key=key)
            if metadata is None:
                response = s3obj.put(Body=obj)
            else:
                response = s3obj.put(Body=obj, Metadata=metadata)
        elif TRANSFER == 'ELASTICACHE':
            self.elasticache_client.set(key, obj)
        elif TRANSFER == 'XDT':
            key = self.XDTclient.Put(payload=obj)

        return key

    def get(self, key):
        log.info("Downloading Object with key '" + key + "' from " + TRANSFER)

        if TRANSFER == 'S3':
            s3obj = self.s3Bucket.Object(key=key)
            response = s3obj.get()
            return response['Body'].read()
        elif TRANSFER == 'ELASTICACHE':
            response = self.elasticache_client.get(key)
            return response
        elif TRANSFER == 'XDT':
            return XDTdst.Get(key, self.XDTconfig)
