#!/bin/bash
#
# Update remote files


set -e -x

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ROOT="$( cd $DIR && cd .. && pwd)"


VERSION=${1:-v0.3.9}
echo "Update Online boutique version to: ${VERSION}"


SERVICES="adservice cartservice checkoutservice currencyservice emailservice paymentservice productcatalogservice recommendationservice shippingservice"

# 1. Delete the files from the current version
rm -rf $SERVICES
rm -rf microservices-demo


# 2. Pull the remote repo
git clone https://github.com/GoogleCloudPlatform/microservices-demo.git

# 3. Checkout the correct version
#    and copy the new files
pushd microservices-demo
git checkout $VERSION

for s in $SERVICES ;
do
  cp -r src/$s ../
done

popd



# ##################
# ## Manual fixes ##

# # No support for google cloud debugger at the moment for arm.
# sed -i 's|google-python-cloud-debugger|#google-python-cloud-debugger|g' recommendationservice/requirements.txt
# sed -i 's|import googleclouddebugger|#import googleclouddebugger|g' recommendationservice/recommendation_server.py
# ##################


# 3. Check if everything still builds
for s in $SERVICES ;
do
  echo "Build ${s} image..."
  make ${s}-image
done

echo "Build all images successfully"



# 4. Check if all functions work with docker-compose

for s in $SERVICES ;
do
  echo "Test ${s} image with docker-compose"

  # Start the function
  docker-compose -f yamls/docker-compose/dc-${s}.yaml up -d --remove-orphans
  sleep 5

  # Invoke it
  ./../../tools/bin/grpcurl -plaintext \
                localhost:50000 helloworld.Greeter.SayHello

  sleep 1
  docker-compose -f yamls/docker-compose/dc-${s}.yaml down --remove-orphans
  sleep 5
done

echo "Invoked all functions successfully"