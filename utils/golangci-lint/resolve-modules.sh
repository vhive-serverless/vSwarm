echo "Resolving modules in $(pwd)"
PATHS=$(find . -mindepth 2 -not -path "*/vendor/*" -type f -name go.mod -printf '{"workdir":"%h"},')
echo "::set-output name=matrix::{\"include\":[${PATHS%?}]}"
