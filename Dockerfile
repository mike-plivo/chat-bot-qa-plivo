FROM debian:bullseye-slim

ARG DEBIAN_FRONTEND=noninteractive

#RUN apk add --no-cache python3 redis py3-pip gcc g++ libc-dev git make python3-dev bash
RUN apt-get update && apt-get install -y --no-install-recommends \
	git \
	curl \
	ca-certificates \
	python3 \
	redis-server \
	python3-pip
RUN rm -rf /var/lib/apt/lists/* || true

WORKDIR /app
# Install dependencies
COPY entrypoint.sh .
COPY requirements.txt .
COPY *.py .
RUN mkdir data || true
RUN pip3 install --no-cache-dir  -r requirements.txt
RUN chmod 755 ./entrypoint.sh

EXPOSE 50505

ENTRYPOINT ["sh", "-c", "./entrypoint.sh"]

