# MIT License
#
# Copyright (c) 2022 Alan Nair and The vHive Ecosystem
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

import argparse
import boto3
import os

AWS_REGION = os.environ.get('AWS_REGION')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_ACCOUNT_ID = os.environ.get('AWS_ACCOUNT_ID')

def create_ecr_repo(name):
    client = boto3.client('ecr')
    try:
        client.create_repository(registryId=AWS_ACCOUNT_ID, repositoryName=name)
    except client.exceptions.RepositoryAlreadyExistsException as e:
        pass

def parse_args():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title='action', dest='action',
            metavar='<action>', required=True)

    parse_create_ecr_repo = subparser.add_parser('create_ecr_repo',
            help='create ECR repository')
    parse_create_ecr_repo.add_argument('-n', '--repo_name',
            metavar='<ECR repo name>', type=str, required=True,
            help='name of the ECR repository to be created')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    if args.action == 'create_ecr_repo':
        create_ecr_repo(name=args.repo_name)
