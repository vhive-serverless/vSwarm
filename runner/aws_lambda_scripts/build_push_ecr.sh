#!/bin/bash
set -e

# BUILD DOCKER IMAGE and PUSH TO AWS ECR

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


DOCKERFILE="${DOCKERFILE:-Dockerfile}"
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-'us-west-1'}
REPO_TAG=${REPO_TAG:-'latest'}

MODE=${MODE:-'--load'}
PLATFORM=${PLATFORM:-'--platform linux/amd64'}

function sanitize() {
  if [ -z "${1}" ]; then
    >&2 echo "Unable to find the ${2}"
    exit 1
  fi
}

function create_ecr_repo() {
  echo "== CHECK REPO EXISTS"
  set +e
  output=$(aws ecr describe-repositories --region ${AWS_DEFAULT_REGION} \
		--repository-names ${REPO_NAME} 2>&1)
  exit_code=$?
  if [ ${exit_code} -ne 0 ]; then
    if echo ${output} | grep -q RepositoryNotFoundException; then
      echo "== REPO DOES NOT EXIST, CREATING.."
      aws ecr create-repository --region ${AWS_DEFAULT_REGION} \
				--repository-name ${REPO_NAME}
      echo "== FINISHED CREATE REPO"
    else
      >&2 echo ${output}
      exit $exit_code
    fi
  else
    echo "== REPO EXISTS, SKIPPING CREATION.."
  fi
  set -e
}

function login(){
	echo "== START LOGIN"
	aws ecr get-login-password --region ${AWS_DEFAULT_REGION} | \
		docker login --username AWS --password-stdin ${ACCOUNT_URL}
	echo "== LOGIN DONE"
}

function docker_build(){
	echo "== START DOCKER BUILD"
	docker buildx build ${PLATFORM} \
		-t ${ACCOUNT_URL}/${REPO_NAME}:${REPO_TAG} \
		--build-arg target_arg=${TARGET} \
		-f ${DOCKERFILE} \
		. ${MODE}
	echo "== DOCKER BUILD DONE"
}

function docker_push_to_ecr() {
  echo "== START PUSH TO ECR"
	docker push ${ACCOUNT_URL}/${REPO_NAME}:${REPO_TAG}
  echo "== FINISHED PUSH TO ECR"
}

sanitize "${AWS_ACCESS_KEY_ID}" "AWS_ACCESS_KEY_ID"
sanitize "${AWS_SECRET_ACCESS_KEY}" "AWS_SECRET_ACCESS_KEY"
sanitize "${AWS_ACCOUNT_ID}" "AWS_ACCOUNT_ID"
sanitize "${REPO_NAME}" "REPO_NAME"
sanitize "${TARGET}" "TARGET"

ACCOUNT_URL="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"

login
docker_build
create_ecr_repo
docker_push_to_ecr
