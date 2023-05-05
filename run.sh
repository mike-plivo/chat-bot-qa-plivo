#!/bin/bash
MYENV="prod"
ARCH="amd64"
case $1 in
	prod|dev|ingest|qdrant)
		MYENV="$1"
	;;
	"*")
		echo "Usage: $0 (prod|dev|ingest|qdrant)"
		echo "	Default is: prod"
		exit 1
	;;
esac

case "$MYENV" in
	"prod")
		[ -z "$OPENAI_API_KEY" ] && echo " * Error: OPENAI_API_KEY is not set" && exit 1
		[ -z "$SLACK_TOKEN_ID" ] && echo " * Error: SLACK_TOKEN_ID is not set" && exit 1
		[ -z "$VECTOR_DATABASE" ] && echo " * Error: VECTOR_DATABASE is not set" && exit 1
		[ -z "$OPENAI_MODEL" ] && OPENAI_MODEL="gpt-3.5-turbo" && echo " * Warning: OPENAI_MODEL is not set, using default: $OPENAI_MODEL"
		extra_args="-p 50505:50505"
		CMD="/bin/bash -c ./start_slackbot.sh"
	;;
	"dev")
		[ -z "$OPENAI_API_KEY" ] && OPENAI_API_KEY="xxxx" && echo " * Warning: OPENAI_API_KEY is not set, using default: $OPENAI_API_KEY"
		[ -z "$SLACK_TOKEN_ID" ] && SLACK_TOKEN_ID="xxxx" && echo " * Warning: SLACK_TOKEN_ID is not set, using default: $SLACK_TOKEN_ID"
		[ -z "$VECTOR_DATABASE" ] && VECTOR_DATABASE="/app/data/codebot.faiss.${ARCH}" && echo " * Warning: VECTOR_DATABASE is not set, using default: $VECTOR_DATABASE"
		[ -z "$OPENAI_MODEL" ] && OPENAI_MODEL="gpt-3.5-turbo" && echo " * Warning: OPENAI_MODEL is not set, using default: $OPENAI_MODEL"
		extra_args="-p 50505:50505"
		CMD="/bin/bash"
	;;
	"ingest")
		[ -z "$OPENAI_API_KEY" ] && echo " * Error: OPENAI_API_KEY is not set" && exit 1
		[ -z "$VECTOR_DATABASE" ] && echo " * Error: VECTOR_DATABASE is not set" && exit 1
		[ -z "$OPENAI_MODEL" ] && OPENAI_MODEL="gpt-3.5-turbo" && echo " * Warning: OPENAI_MODEL is not set, using default: $OPENAI_MODEL"
		CMD="/bin/bash -c ./start_ingest.sh"
	;;
	"qdrant")
		extra_args="-p 6334:6334"
		CMD="/bin/bash -c ./start_qdrant.sh"
	;;
esac
echo

if [ ! -d "${PWD}/data" ]; then
	mkdir -p ${PWD}/data
fi

docker run --platform "linux/${ARCH}" \
	--rm \
	-ti \
	-e SLACK_TOKEN_ID="$SLACK_TOKEN_ID" \
	-e OPENAI_API_KEY="$OPENAI_API_KEY" \
	-e OPENAI_MODEL="$OPENAI_MODEL" \
	-e ARCH="$ARCH" \
	-e ENV="$MYENV" \
	-v "${PWD}/data:/app/data" $extra_args \
	plivo/askme $CMD

