# Support for the AWS Lambda Platform

This document discusses the support offered in this repository to running benchmarks as containerized functions on AWS Lambda. Currently, AWS Lambda support has been implemented for the _map-reduce_ benchmark. Please note that tracing is not supported on AWS Lambda for any benchmark currently.

## Directory Structure for Benchmarks that implement Multi-Cloud Support

Containers built for different platforms may need to be built with different commands, therefore, benchmarks that implement multi-cloud support shall keep separate _Dockerfiles_ for each platform in the `docker/` folder in the benchmark directory. `docker/Dockerfile` shall be used to run benchmarks locally or on knative, while `docker/Dockerfile.Lambda` shall be used for containers intended to be deployed as functions on AWS Lambda.

Containers intended for different platforms may have require different modules or requirements, so these may optionally be maintained as separate .txt files in a folder (for examples, see _requirements/*.txt_ in the _map-reduce_ benchmark directory).

## AWS Lambda Support Scripts

Actions pertaining to AWS Lambda support are implemented in `runner/aws_lambda_scripts/aws_actions.py`. Do `python aws_actions.py -h` to see usage.

### Environment Variables

AWS Account Credentials are required by the script to authenticate to and perform actions on AWS Lambda. These credentials are to be provided as environment variables to the script. The following environment variables must be properly set/exported before running the scripts to ensure smooth execution.
  - `AWS_ACCESS_KEY_ID` or `AWS_ACCESS_KEY`: A 20-character long string that constitutes your AWS account's Access Key ID. [How to find out my Access Key ID?](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)
  - `AWS_SECRET_KEY` or `AWS_SECRET_ACCESS_KEY`: Your AWS account's secret access key. [How to find out my Secret Key?](https://docs.aws.amazon.com/powershell/latest/userguide/pstools-appendix-sign-up.html)
  - `AWS_REGION` or `AWS_DEFAULT_REGION`: The Region Code of the physical AWS datacenter which we use. [How to find out the right Region ID?](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html)
  - `AWS_ACCOUNT_ID`: The 12-digit number which you can use to sign in to the AWS Console. [How to find out my Account ID?](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html)

### Building and Pushing Container Images

To deploy container images as functions on AWS Lambda, we first need to build them, and then push them onto **AWS ECR** which is AWS's Docker container registry that makes it easy to store, share, and deploy container images. While building images, tag them with your ECR namespace URI (i.e. `$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/name:tag`). For instance:
```
$ docker buildx build -platform linux/arm64 \
  -t $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/newfunc:latest \
  -f docker/Dockerfile.Lambda \
  ../.. --load
```
The next step is to push the container to an AWS ECR repository.
First Login to AWS ECR via Docker. For this install _awscli_ if not already installed (`sudo apt-get install awscli` on Debian-based distros).
```
$ aws ecr get-login-password --region $(AWS_REGION) | \
  docker login --username AWS --password-stdin \
  $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com
```
Then we need to create an ECR repository. `aws_actions.py` may be used for this.
```
$ python aws_actions.py create_ecr_repo --repo_name newfunc
```
The final step is to push the built container to the newly created repository.
```
$ docker push $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/newfunc:latest
```

### Deploying Lambda Function from ECR container

Once we have pushed a container to AWS ECR we may deploy it as a function to AWS Lambda.
For example, suppose we want to the deploy `newfunc` image from the previous step as a Lambda function `NewFuncLambda`. It needs to access **AWS S3** buckets as well as to invoke other AWS Lambda functions in the course of its execution. It needs to be configured with the environment variables `KEY1=VAL1` and `KEY2=VAL2`.
```
$ python aws_actions.py --repo_name newfunc --repo_tag latest \
  --function_name NewFuncLambda --policies access_s3,invoke_function \
  --envmap '{"KEY1":"VAL1","KEY2":"VAL2"}'
```

### Invoking Lambda Function

Once Deployed, we may invoke the Lambda Function using the same script. Suppose we need to invoke it with the event JSON `'{k1 : v1}'`.
```
$ python aws_actions.py --function_name NewFuncLambda --payload '{"K1":"V1"}'
```
