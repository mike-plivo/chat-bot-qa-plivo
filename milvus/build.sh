#!/bin/bash
ARCH=amd64
set -x
docker build \
	-f Dockerfile \
	--platform linux/${ARCH} \
	-t plivo/milvuslite .
