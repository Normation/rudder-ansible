#!/bin/sh

set -e

export COLLECTION_VERSION="$(yq .version galaxy.yml | tr -d '"')"

ansible-galaxy collection build .
ansible-galaxy collection publish ./rudder-ansible-${COLLECTION_VERSION}.tar.gz --api-key "${1}"

