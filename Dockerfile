FROM python:3.13-slim
WORKDIR /
ARG PIP_CACHE_DIR=/tmp/.cache/pip
ENV PIP_CACHE_DIR=$PIP_CACHE_DIR
RUN mkdir -p $PIP_CACHE_DIR
COPY redis-benchmark/src/redis_benchmark/ ./
COPY redis-benchmark/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
