#!/bin/sh

echo "Creating Redis Cluster..."
yes "yes" | redis-cli --cluster create \
  127.0.0.1:6379 127.0.0.1:6380 127.0.0.1:6381 \
  --cluster-replicas 0

echo "Cluster created successfully!"
