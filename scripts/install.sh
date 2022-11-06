#!/usr/bin/env bash
#
# Install cluster management related packaging
#
set -e

TERRAFORM_VERSION=1.3.3

if [ ! -f /usr/local/bin/terraform ]
then
    echo "Installing Terraform version ${TERRAFORM_VERSION}"
    wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip 2>/dev/null
    unzip -o terraform_${TERRAFORM_VERSION}_linux_amd64.zip -d /usr/local/bin
fi
mkdir -p ~/.terraform.d/plugins
