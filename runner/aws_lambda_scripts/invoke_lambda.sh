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
    --cli-binary-format raw-in-base64-out \
    --payload "${PAYLOAD}" --log-type Tail outfile.txt
fi
echo "== DONE INVOKING LAMBDA FUNCTION"
