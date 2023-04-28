FROM debian:bullseye-slim

#RUN apk add --no-cache python3 redis py3-pip gcc g++ libc-dev git make python3-dev bash
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	cmake \
	make \
	swig \
	git \
	curl \
	ca-certificates \
	python3 \
	python3-pip \
	python3-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Install dependencies
COPY requirements.txt .
COPY *.py .

RUN mkdir data
COPY data/codebot.faiss data/codebot.faiss
# install numexpr first to cache docker build
RUN pip3 install --no-cache-dir  $(grep numexpr requirements.txt |head -n 1)
# install numpy first to cache docker build
RUN pip3 install --no-cache-dir  $(grep numpy requirements.txt |head -n 1)
# install other dependencies
RUN grep -v numexpr requirements.txt | grep -v numpy > requirements2.txt
RUN pip3 install --no-cache-dir  -r requirements2.txt
RUN rm -f requirements2.txt || true

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]

