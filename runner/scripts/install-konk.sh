#!/usr/bin/env bash

set -eo pipefail

KNATIVE_NET=${KNATIVE_NET:-kourier}

echo -e "✅ Checking dependencies... \033[0m"
STARTTIME=$(date +%s)
/tmp/scripts/01-kind.sh
echo -e "🍿 Installing Knative Serving... \033[0m"
/tmp/scripts/02-serving.sh
echo -e "🔌 Installing Knative Serving Networking Layer ${KNATIVE_NET}... \033[0m"
if [[ "$KNATIVE_NET" == "kourier" ]]; then
    /tmp/scripts/02-kourier.sh
else
    /tmp/scripts/02-contour.sh
fi

# Setup Knative DOMAIN DNS
INGRESS_HOST="127.0.0.1"
KNATIVE_DOMAIN=$INGRESS_HOST.nip.io
kubectl patch configmap -n knative-serving config-domain -p "{\"data\": {\"$KNATIVE_DOMAIN\": \"\"}}"

DURATION=$(($(date +%s) - $STARTTIME))
echo -e "\033[0;92m 🚀 Knative install took: $(($DURATION / 60))m$(($DURATION % 60))s \033[0m"
echo -e "\033[0;92m 🎉 Now have some fun with Serverless and Event Driven Apps \033[0m"