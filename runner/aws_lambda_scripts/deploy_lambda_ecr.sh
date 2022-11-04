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
ECR_REPO_TAG=${REPO_TAG:-'latest'}
ENVIRONMENT_VARIABLE_MAP=${ENVIRONMENT_VARIABLE_MAP:-"{IS_LAMBDA=true}"}

function sanitize() {
	if [ -z "${1}" ]; then
		>&2 echo "Unable to find the ${2}"
		exit 1
	fi
}

create_role(){
	echo "== BEGIN ROLE CREATION"
	set +e
	ROLE_NAME=${LAMBDA_FUNCTION_NAME}-role

	output=$(aws iam get-role --role-name ${ROLE_NAME} 2>&1)
	exit_code=$?
	if [ ${exit_code} -ne 0 ]; then
		if echo ${output} | grep -q NoSuchEntity; then
			echo "== ROLE DOES NOT EXIST, CREATING.."
			aws iam create-role --role-name ${ROLE_NAME} \
				--assume-role-policy-document file://${TRUST_FILE}
			echo "== CREATED ROLE"
			sleep 5
		else
			>&2 echo ${output}
			exit $exit_code
		fi
	else
		echo "== ROLE EXISTS, SKIPPING CREATION.."
	fi

	set -e
	echo "== DONE ROLE CREATION"
}

attach_policies_to_role(){
	set +e

	if [ -z "${POLICY_FILES}" ]; then
		# no policies to attach - do nothing
		true
	else
		for policy_file in ${POLICY_FILES//,/ }
		do
			policy_name=$(basename ${policy_file} .json)

			output=$(aws iam get-role-policy --role-name ${ROLE_NAME} \
				--policy-name ${policy_name} 2>&1)
			exit_code=$?
			if [ ${exit_code} -ne 0 ]; then
				if echo ${output} | grep -q NoSuchEntity; then
					echo "== ADDING POLICY ${policy_name} TO ROLE.."
					aws iam create-policy --policy-name ${policy_name} \
						--policy-document file://${policy_file}
					sleep 5
					aws iam attach-role-policy --role-name ${ROLE_NAME} --policy-arn \
						arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${policy_name}
					sleep 5
				else
					>&2 echo ${output}
		      exit $exit_code
				fi
			else
				echo "== POLICY ${policy_name} ALREADY ATTACHED TO ROLE, SKIPPING.."
			fi

		done
	fi

	echo "== ADDING POLICY AWSLambdaBasicExecution"
	aws iam attach-role-policy --role-name ${ROLE_NAME} --policy-arn \
		arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
	sleep 5

	set -e
}

publish_function(){
	echo "== BEGIN LAMBDA FUNCTION DEPLOYMENT FROM ECR CONTAINER"
	set +e
	ECR_CONTAINER_URI=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_DEFAULT_REGION}.amazonaws.com/${ECR_REPO_NAME}:${ECR_REPO_TAG}

	output=$(aws lambda get-function --function-name ${LAMBDA_FUNCTION_NAME} 2>&1)
	exit_code=$?
	if [ ${exit_code} -ne 0 ]; then
		if echo ${output} | grep -q ResourceNotFoundException; then
			echo "== FUNCTION DOES NOT EXIST, CREATING.."
			aws lambda create-function --function-name ${LAMBDA_FUNCTION_NAME} \
				--code ImageUri=${ECR_CONTAINER_URI} --package-type Image \
				--role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME} \
				--environment Variables=${ENVIRONMENT_VARIABLE_MAP} --timeout 120
			echo "== CREATED FUNCTION"
			sleep 30
		else
			>&2 echo ${output}
			exit $exit_code
		fi
	else
		echo "== FUNCTION EXISTS, UPDATING.."
		aws lambda update-function-code --function-name ${LAMBDA_FUNCTION_NAME} \
			--image-uri ${ECR_CONTAINER_URI}
		sleep 30
		aws lambda update-function-configuration \
			--function-name ${LAMBDA_FUNCTION_NAME} \
			--role arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME} \
			--environment Variables=${ENVIRONMENT_VARIABLE_MAP} --timeout 120
		echo "== UPDATED FUNCTION"
		sleep 30
  fi

	set -e
	echo "== DONE LAMBDA FUNCTION DEPLOYMENT FROM ECR CONTAINER"
}

sanitize "${AWS_ACCESS_KEY_ID}" "AWS_ACCESS_KEY_ID"
sanitize "${AWS_SECRET_ACCESS_KEY}" "AWS_SECRET_ACCESS_KEY"
sanitize "${AWS_ACCOUNT_ID}" "AWS_ACCOUNT_ID"
sanitize "${ECR_REPO_NAME}" "ECR_REPO_NAME"
sanitize "${LAMBDA_FUNCTION_NAME}" "LAMBDA_FUNCTION_NAME"
sanitize "${TRUST_FILE}" "TRUST_FILE"


create_role
attach_policies_to_role
publish_function
