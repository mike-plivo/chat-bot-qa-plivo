#!/bin/bash
ARCH=amd64
DATA_DIR=/data/milvus

docker run --platform "linux/${ARCH}" \
	--rm \
	-ti \
	-e DATA_DIR=${DATA_DIR} \
	-v "${PWD}/data:/data" \
	plivo/milvuslite

