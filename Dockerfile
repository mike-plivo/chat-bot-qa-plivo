FROM debian:bullseye-slim

#RUN apk add --no-cache python3 redis py3-pip gcc g++ libc-dev git make python3-dev bash
RUN apt-get update && apt-get install -y --no-install-recommends \
	#build-essential \
	#cmake \
	#make \
	#swig \
	git \
	curl \
	ca-certificates \
	python3 \
	python3-pip
	#python3-dev &&
RUN rm -rf /var/lib/apt/lists/* || true

WORKDIR /app
# Install dependencies
COPY requirements.txt .
COPY *.py .
RUN mkdir data
COPY data/codebot.faiss data/codebot.faiss
RUN pip3 install --no-cache-dir  -r requirements.txt

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]

