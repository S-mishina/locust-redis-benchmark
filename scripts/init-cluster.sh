#!/bin/sh

echo "Waiting for Redis nodes to start..."

for node in redis-node1:6379 redis-node2:6379 redis-node3:6379; do
  while ! redis-cli -h $(echo $node | cut -d':' -f1) -p $(echo $node | cut -d':' -f2) ping > /dev/null 2>&1; do
    echo "Waiting for Redis node $node to be ready..."
    sleep 2
  done
  echo "PONG"
  echo "Redis node $node is ready."
done

echo "Creating Redis cluster..."
echo "yes" | redis-cli --cluster create \
  172.21.0.2:6379 172.21.0.3:6379 172.21.0.4:6379 \
  --cluster-replicas 0

echo "Redis cluster created successfully."
