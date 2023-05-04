FROM debian:bullseye-slim

ARG DEBIAN_FRONTEND=noninteractive

#RUN apk add --no-cache python3 redis py3-pip gcc g++ libc-dev git make python3-dev bash
RUN apt-get update && apt-get install -y --no-install-recommends \
	git \
	curl \
	ca-certificates \
	redis-server \
	python3 \
	python3-pip
RUN rm -rf /var/lib/apt/lists/* || true

WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir  -r requirements.txt
COPY ./entrypoint.sh .
RUN chmod 755 ./entrypoint.sh
RUN mkdir /data || true

EXPOSE 19530

ENTRYPOINT ["bash", "-c", "./entrypoint.sh"]
