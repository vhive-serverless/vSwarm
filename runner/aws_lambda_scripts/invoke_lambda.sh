#!/bin/bash
set -e

# DEPLOY LAMBDA FUNCTION FROM ECR CONTAINER

#######################
# WORKING DIRECTORY is vSwarm ROOT directory (../..)
# All paths are relative to WORKING DIRECTORY
#
# On platforms such as github workflows, Working Directory is already set
# and awscli is already installed
# On such platforms, env var WORKDIR_SET must be set to some value.
#
# On other platforms (eg. if you are running locally), first we must
# cd to WORKING DIRECTORY and install awscli
# Make sure that env var WORKDIR_SET is not set.
# see below.
if [[ -z "${WORKDIR_SET}" ]]; then
  cd ../..
	pip install -U awscli
fi
#######################

AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-'us-west-1'}

function sanitize() {
  if [ -z "${1}" ]; then
    >&2 echo "Unable to find the ${2}"
    exit 1
  fi
}

sanitize "${AWS_ACCESS_KEY_ID}" "AWS_ACCESS_KEY_ID"
sanitize "${AWS_SECRET_ACCESS_KEY}" "AWS_SECRET_ACCESS_KEY"
sanitize "${AWS_ACCOUNT_ID}" "AWS_ACCOUNT_ID"
sanitize "${LAMBDA_FUNCTION_NAME}" "LAMBDA_FUNCTION_NAME"

echo "== INVOKING LAMBDA FUNCTION"
if [ -z "${PAYLOAD}" ]; then
	aws lambda invoke --function-name ${LAMBDA_FUNCTION_NAME} \
		--log-type Tail outfile.txt
else
	aws lambda invoke --function-name ${LAMBDA_FUNCTION_NAME} \
		--payload ${PAYLOAD} --log-type Tail outfile.txt
fi
echo "== DONE INVOKING LAMBDA FUNCTION"
