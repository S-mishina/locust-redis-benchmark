FROM python:3.13-slim
COPY dist/locust_cache_benchmark-*.whl /
RUN apt -y update && apt --no-install-recommends install -y gcc && pip install ./locust_cache_benchmark-*.whl && apt-get clean && rm -rf /var/lib/apt/lists/*
