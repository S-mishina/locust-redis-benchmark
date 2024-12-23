from locust import HttpUser, TaskSet, task, between
import redis
import random

class RedisTaskSet(TaskSet):
  def on_start(self):
    self.redis_client = redis.StrictRedis(host='redis-node1', port=6379, db=0)
    self.redis_client = redis.StrictRedis(
      host='redis-node1', port=6379, db=0, decode_responses=True
    )

  @task
  def set_value(self):
    key = f"key_{random.randint(1, 10000)}"
    value = f"value_{random.randint(1, 10000)}"
    self.redis_client.set(key, value)

  @task
  def get_value(self):
    key = f"key_{random.randint(1, 10000)}"
    self.redis_client.get(key)

  @task
  def failover(self):
    # Simulate a failover by switching to a different Redis instance
    self.redis_client = redis.StrictRedis(host='localhost', port=6380, db=0)

class RedisUser(HttpUser):
  tasks = [RedisTaskSet]
  wait_time = between(1, 5)
