echo "Resolving modules in $(pwd)"
PATHS=$(find . -mindepth 2 -type f -name go.mod ! -path "./tools/knative-eventing-tutorial/*" ! -path "*/vendor/*" -printf '{"workdir":"%h"},')
echo "::set-output name=matrix::{\"include\":[${PATHS%?}]}"
