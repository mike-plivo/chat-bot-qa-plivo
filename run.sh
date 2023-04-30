#!/bin/bash
case $1 in
	"prod"|"dev"|"ingest")
	;;
	"*")
		echo "Usage: $0 (prod|dev) [amd64|arm64]"
		echo "	Default is amd64"
		exit 1
	;;
esac

case $2 in
	"arm64")
		ARCH=$2
	;;
	"*")
		ARCH="amd64"
	;;
esac

docker run --platform linux/${ARCH} \
	-ti \
	-e SLACK_ENTERPRISE_ID="test" \
	-e SLACK_TOKEN_ID="test" \
	-e OPENAI_API_KEY="$OPENAI_API_KEY" \
	-e OPENAI_MODEL="gpt-3.5-turbo" \
	-e VECTOR_DATABASE="data/codebot.faiss.${ARCH}" \
	-e ARCH="$ARCH" \
	-e ENV="$1" \
	-v "${PWD}/data:/app/data" \
	plivo/askme
