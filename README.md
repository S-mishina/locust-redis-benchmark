
# redis-benchmark

**redis-benchmark** is a tool designed to test the performance of Redis clusters. It uses Locust for load testing and measures metrics such as response time and cache hit rate for Redis clusters.

## Features

- Executes load tests on Redis clusters
- Allows configuration of parameters such as cache hit rate, value size, and TTL
- Displays test results in real-time

## Supported Environments

This tool currently supports Redis (Cluster Mode only).

## Processing Flow

![architecture](./image/architecture.png)

## Installation

### Local Machine

Install the necessary dependencies using the following command:

```sh
pip install -r redis-benchmark/requirements.txt
```

### Container

Build and run the Docker container using the command below:

```sh
docker pull ghcr.io/s-mishina/locust-redis-benchmark:latest
```

## Usage

### Local Machine

To initialize a Redis cluster, run the following command:

```sh
python redis-benchmark/src/redis_benchmark/main.py init redis -f <hostname> -p <port>
```

To execute a load test on a Redis cluster, use the command:

```sh
python redis-benchmark/src/redis_benchmark/main.py loadtest redis -f <hostname> -p <port> -r <hit_rate> -d <duration> -c <connections> -n <requests> -k <value_size> -t <ttl>
```

### Container

To initialize a Redis cluster, use the following command:

```sh
docker run --rm -it ghcr.io/s-mishina/locust-redis-benchmark:latest python redis-benchmark/src/redis_benchmark/main.py init redis -f <hostname> -p <port>
```

To execute a load test on a Redis cluster, run:

```sh
docker run --rm -it ghcr.io/s-mishina/locust-redis-benchmark:latest python redis-benchmark/src/redis_benchmark/main.py loadtest redis -f <hostname> -p <port> -r <hit_rate> -d <duration> -c <connections> -n <requests> -k <value_size> -t <ttl>
```

## Parameters

- `--fqdn, -f`: Hostname of the Redis server (default: `localhost`)
- `--port, -p`: Port of the Redis server (default: `6379`)
- `--hit-rate, -r`: Cache hit rate (default: `0.5`)
- `--duration, -d`: Test duration in seconds (default: `60`)
- `--connections, -c`: Number of concurrent connections (default: `1`)
- `--requests, -n`: Number of requests to send (default: `1000`)
- `--value-size, -k`: Value size in KB (default: `1`)
- `--ttl, -t`: Time-to-live of the key in seconds (default: `60`)
