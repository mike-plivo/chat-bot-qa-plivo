FROM qdrant/qdrant:v1.1.2

ARG DEBIAN_FRONTEND=noninteractive

#RUN apk add --no-cache python3 redis py3-pip gcc g++ libc-dev git make python3-dev bash
RUN apt-get update && apt-get install -y --no-install-recommends \
	git \
	curl \
	procps \
	ca-certificates \
	redis-server \
	python3 \
	python3-pip
RUN rm -rf /var/lib/apt/lists/* || true

WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir  -r requirements.txt
RUN mkdir data || true
COPY start_slackbot.sh .
COPY start_qdrant.sh .
COPY start_ingest.sh .
COPY local_test.sh .
COPY qdrant.config.yml .
COPY *.py .
RUN chmod 755 ./start_slackbot.sh ./start_qdrant.sh ./start_ingest.sh ./local_test.sh

CMD ["bash", "-c", "./start_slackbot.sh"]

