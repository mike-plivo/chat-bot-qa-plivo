#!/bin/bash
ARCH="amd64"

set -x
docker build \
	-f Dockerfile \
	--platform linux/${ARCH} \
	--build-arg ARCH=${ARCH} \
	-t plivo/askme .
