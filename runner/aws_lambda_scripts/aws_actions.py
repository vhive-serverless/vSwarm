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
import json
import os
import sys
import time

AWS_REGION = os.environ.get('AWS_REGION')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.environ.get('AWS_SECRET_KEY')
AWS_ACCOUNT_ID = os.environ.get('AWS_ACCOUNT_ID')

policy_jsons = {
    "trust" : json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }),
    "access_s3" : json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:*",
                    "s3-object-lambda:*"
                ],
                "Resource": "*"
            }
        ]
    }),
    "invoke_function" : json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "lambda:InvokeFunction"
                ],
                "Resource": [
                    "*"
                ]
            }
        ]
    })
}

def create_ecr_repo(name):
    client = boto3.client('ecr')
    try:
        client.create_repository(registryId=AWS_ACCOUNT_ID, repositoryName=name)
    except client.exceptions.RepositoryAlreadyExistsException:
        pass

def create_role(role):
    client = boto3.client('iam')
    try:
        client.get_role(RoleName=role)
    except client.exceptions.NoSuchEntityException:
        client.create_role(RoleName=role, AssumeRolePolicyDocument=policy_jsons["trust"])
        time.sleep(5)

def attach_policies_to_role(role, policies):
    client = boto3.client('iam')
    if policies:
        policies = policies.split(',')
        for policy in policies:
            if policy not in policy_jsons:
                sys.exit('Policy %s Not Recognized' % (policy))
            try:
                client.get_role_policy(RoleName=role, PolicyName=policy)
            except client.exceptions.NoSuchEntityException:
                arn = 'arn:aws:iam::%s:policy/%s' % (AWS_ACCOUNT_ID, policy)
                try:
                    client.get_policy(PolicyArn=arn)
                except client.exceptions.NoSuchEntityException:
                    client.create_policy(PolicyName=policy, PolicyDocument=policy_jsons[policy])
                    time.sleep(5)

                client.attach_role_policy(RoleName=role, PolicyArn=arn)
                time.sleep(5)

    basicRoleArn = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
    client.attach_role_policy(RoleName=role, PolicyArn=basicRoleArn)
    time.sleep(5)

def publish_function(role, repo, tag, lambdafn, env):
    client = boto3.client('lambda')
    uri = '%s.dkr.ecr.%s.amazonaws.com/%s:%s' % (AWS_ACCOUNT_ID, AWS_REGION, repo, tag)
    roleArn = 'arn:aws:iam::%s:role/%s' % (AWS_ACCOUNT_ID, role)
    try:
        client.get_function(FunctionName=lambdafn)
    except client.exceptions.ResourceNotFoundException:
        client.create_function(FunctionName=lambdafn, Role=roleArn,
                Code={'ImageUri': uri}, Timeout=120, PackageType='Image',
                Environment={'Variables': env})
        time.sleep(30)
    else:
        client.update_function_code(FunctionName=lambdafn, ImageUri=uri)
        time.sleep(30)
        client.update_function_configuration(FunctionName=lambdafn,
                Role=roleArn, Timeout=120, Environment={'Variables': env})
        time.sleep(15)

def deploy_lambdafn_from_ecr(repo, tag, lambdafn, policies, env):
    role = lambdafn + '-role'
    create_role(role)
    attach_policies_to_role(role, policies)
    publish_function(role, repo, tag, lambdafn, env)

def invoke_lambdafn(lambdafn, payload):
    client = boto3.client('lambda')
    response = client.invoke(FunctionName=lambdafn, LogType='Tail', Payload=payload)
    print(response)

def parse_args():
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(title='action', dest='action',
            metavar='<action>', required=True)

    parse_create_ecr_repo = subparser.add_parser('create_ecr_repo',
            help='Create ECR repository')
    parse_create_ecr_repo.add_argument('-n', '--repo_name',
            metavar='<ECR repo name>', type=str, required=True,
            help='Name of the ECR repository to be created')

    parser_deploy_lambdafn_from_ecr = subparser.add_parser(
            'deploy_lambdafn_from_ecr',
            help='Deploy Lambda Function from ECR repository')
    parser_deploy_lambdafn_from_ecr.add_argument('-n', '--repo_name',
            metavar='<ECR repo name>', type=str, required=True,
            help='Name of the ECR repository from which'\
                'container is to be deployed as Lambda function')
    parser_deploy_lambdafn_from_ecr.add_argument('-t', '--repo_tag',
            metavar='<ECR container tag>', type=str, default='latest',
            help='Tag of the container present in the ECR repository'\
                'which is to be deployed as Lambda function')
    parser_deploy_lambdafn_from_ecr.add_argument('-f', '--function_name',
            metavar='<Lambda function name>', type=str, required=True,
            help='Name of the Lambda function to be deployed')
    parser_deploy_lambdafn_from_ecr.add_argument('-p', '--policies',
            metavar='<Policies>', type=str,
            help='Comma-Separated List of Policies to attach'\
                'Supported Policies : [access_s3, invoke_function]')
    parser_deploy_lambdafn_from_ecr.add_argument('-e', '--envmap',
            metavar='<Environment Variable Mapping>', type=str,
            default='{"IS_LAMBDA":"true"}', help='Environment Variable Mapping'\
                'to be configured for the deployed Lambda function')

    parser_invoke_lambdafn = subparser.add_parser('invoke_lambdafn',
            help='Invoke Lambda function')
    parser_invoke_lambdafn.add_argument('-f', '--function_name',
            metavar='<Lambda function name>', type=str, required=True,
            help='Name of the Lambda function to be invoked')
    parser_invoke_lambdafn.add_argument('-p', '--payload',
            metavar='<Invocation payload>', type=str, default='{}',
            help='JSON event trigger for Lambda function')

    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    if args.action == 'create_ecr_repo':
        create_ecr_repo(name=args.repo_name)

    if args.action == 'deploy_lambdafn_from_ecr':
        deploy_lambdafn_from_ecr(repo=args.repo_name, tag=args.repo_tag,
                lambdafn=args.function_name, policies=args.policies,
                env=json.loads(args.envmap))

    if args.action == 'invoke_lambdafn':
        invoke_lambdafn(lambdafn=args.function_name, payload=args.payload)
