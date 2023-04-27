FROM alpine:latest as build

RUN apk add --no-cache python3 redis py3-pip gcc g++ libc-dev git make python3-dev bash

WORKDIR /app
# Install dependencies
COPY requirements.txt .
COPY *.py .

RUN mkdir data
COPY data/codebot.faiss data/codebot.faiss
RUN pip3 install --ignore-installed -r requirements.txt

EXPOSE 50505

ENTRYPOINT ["gunicorn", "app:app"]

