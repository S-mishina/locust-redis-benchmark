FROM python:3.13-slim
WORKDIR /locust-cache-benchmark
ARG PIP_CACHE_DIR=/tmp/.cache/pip
ENV PIP_CACHE_DIR=$PIP_CACHE_DIR
ENV PYTHONPATH=/locust-cache-benchmark/cache_benchmark/src
RUN mkdir -p $PIP_CACHE_DIR
COPY /  /locust-cache-benchmark
COPY cache_benchmark/requirements.txt requirements.txt
RUN apt-get update && apt-get install -y gcc && pip install --no-cache-dir -r requirements.txt
