#!/bin/bash
MYENV="prod"
case $1 in
	"prod"|"dev"|"ingest")
		MYENV="$1"
	;;
	"*")
		echo "Usage: $0 (prod|dev) [amd64|arm64]"
		echo "	Default is: prod amd64"
		exit 1
	;;
esac

ARCH="amd64"
case $2 in
	"arm64"|"amd64")
		ARCH=$2
	;;
	"*")
		echo "Invalid architecture $2"
		exit 1
	;;
esac


if [ -z "$OPENAI_API_KEY" ]; then
	echo "OPENAI_API_KEY is not set"
	exit 1
fi

if [ "$MYENV" = "prod" ] || [ "$MYENV" = "dev" ]; then
	extra_args="-p 50505:50505"
fi

set -x
docker run --platform "linux/${ARCH}" \
	-ti \
	-e SLACK_ENTERPRISE_ID="test" \
	-e SLACK_TOKEN_ID="test" \
	-e OPENAI_API_KEY="$OPENAI_API_KEY" \
	-e OPENAI_MODEL="gpt-3.5-turbo" \
	-e VECTOR_DATABASE="data/codebot.faiss.${ARCH}" \
	-e ARCH="$ARCH" \
	-e ENV="$MYENV" \
	-v "${PWD}/data:/app/data" $extra_args \
	plivo/askme
