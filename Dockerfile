FROM python:3.13-slim
WORKDIR /
ARG PIP_CACHE_DIR=/tmp/.cache/pip
ENV PIP_CACHE_DIR=$PIP_CACHE_DIR
RUN mkdir -p $PIP_CACHE_DIR
COPY cache_benchmark/src/cache_benchmark/ ./
COPY cache_benchmark/requirements.txt ./
RUN apt-get update && apt-get install -y gcc && pip install --no-cache-dir -r requirements.txt
