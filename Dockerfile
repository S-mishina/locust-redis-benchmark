FROM python:3.13-slim
COPY dist/locust_cache_benchmark-*.whl /
RUN apt-get update && apt-get install -y gcc
RUN pip install ./locust_cache_benchmark-*.whl
