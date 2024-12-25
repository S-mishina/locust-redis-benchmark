FROM python:3.13-slim
WORKDIR /
COPY redis-benchmark/src/redis_benchmark/ ./
COPY redis-benchmark/requirements.txt ./
RUN apt-get update && apt-get install -y gcc && pip install -r requirements.txt
