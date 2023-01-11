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
import boto3
import redis
import destination as XDTdst
import source as XDTsrc
import utils as XDTutil

S3 = "S3"
XDT = "XDT"
ELASTICACHE = "ELASTICACHE"

LAMBDA = os.environ.get('IS_LAMBDA', 'no').lower() in ['true', 'yes', '1']
TRANSFER = os.environ.get('TRANSFER_TYPE', S3)

supportedTransfers = [S3, ELASTICACHE, XDT]


class Storage:
    def __init__(self, bucket="", transferConfig=None, transferType=""):
        self.bucket = bucket
        if transferType == "":
            self.transferType = TRANSFER
        else:
            self.transferType = transferType

        if self.transferType not in supportedTransfers:
            errmsg = "Error in Environment Variable TRANSFER_TYPE: "
            errmsg += "TRANSFER_TYPE should contain one of " + str(supportedTransfers)
            sys.exit(errmsg)
        
        if self.transferType == S3:
            if LAMBDA:
                self.s3Bucket = boto3.resource(service_name='s3').Bucket(bucket)
            else:
                self.s3Bucket = boto3.resource(
                    service_name='s3',
                    region_name=os.environ.get('AWS_REGION'),
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_KEY')
                ).Bucket(bucket)
        elif self.transferType == ELASTICACHE:
            host, port = bucket.split(":")
            self.elasticache_client = redis.Redis(host=host, port=port)
        elif self.transferType == XDT:
            if transferConfig is None:
                log.fatal("Transfer Config cannot be empty for XDT transfers")
            self.XDTconfig = transferConfig
            self.XDTclient = XDTsrc.XDTclient(config=self.XDTconfig)

    def put(self, key, obj, metadata=None):
        log.info("Uploading Object with key '" + key + "' to " + self.transferType)

        if self.transferType == S3:
            s3obj = self.s3Bucket.Object(key=key)
            if metadata is None:
                response = s3obj.put(Body=obj)
            else:
                response = s3obj.put(Body=obj, Metadata=metadata)
        elif self.transferType == ELASTICACHE:
            self.elasticache_client.set(key, obj)
        elif self.transferType == XDT:
            key = self.XDTclient.Put(payload=obj)

        return key

    def get(self, key):
        log.info("Downloading Object with key '" + key + "' from " + self.transferType)

        if self.transferType == S3:
            s3obj = self.s3Bucket.Object(key=key)
            response = s3obj.get()
            return response['Body'].read()
        elif self.transferType == ELASTICACHE:
            response = self.elasticache_client.get(key)
            return response
        elif self.transferType == XDT:
            payload = XDTdst.BroadcastGet(key, self.XDTconfig)
            log.info("[storage] received xdt payload %d bytes", len(payload))
            return payload
