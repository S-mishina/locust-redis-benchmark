import os
import time
from locust import HttpUser, TaskSet, task, between
from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
import random

class RedisTaskSet(TaskSet):
    def on_start(self):
        startup_nodes = [
            ClusterNode("localhost", 7100)
        ]
        print(f"Connecting to Redis cluster with nodes: {startup_nodes}")
        try:
            self.redis_client = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=True,
                ssl=False,
                ssl_cert_reqs=None,
                socket_timeout=1
            )
            print("Redis client initialized successfully")
        except ClusterDownError:
            print("Cluster is down. Retrying...")
            self.redis_client = None
        except Exception as e:
            print(f"Unexpected error during Redis initialization: {e}")
            self.redis_client = None

    @task
    def set_value(self):
        key = f"key_{random.randint(1, 10000)}"
        value = f"value_{random.randint(1, 10000)}"
        start_time = time.perf_counter()
        try:
            result = self.redis_client.set(key, value)
            total_time = (time.perf_counter() - start_time) * 1000
            # 成功イベントを発火
            self.user.environment.events.request.fire(
                request_type="Redis",
                name="set_value",
                response_time=total_time,
                response_length=0,
                context={},  # 任意の情報を付加できます
                exception=None,  # エラーがない場合は None
            )
            print(f"Set key: {key}, result: {result}")
        except Exception as e:
            total_time = (time.perf_counter() - start_time) * 1000
            # 失敗イベントを発火
            self.user.environment.events.request.fire(
                request_type="Redis",
                name="set_value",
                response_time=total_time,
                response_length=0,
                context={},
                exception=e,  # エラー情報を付加
            )

    @task
    def get_value(self):
        key = f"key_{random.randint(1, 10000)}"
        start_time = time.perf_counter()
        try:
            result = self.redis_client.get(key)
            total_time = (time.perf_counter() - start_time) * 1000
            # 成功イベントを発火
            self.user.environment.events.request.fire(
                request_type="Redis",
                name="get_value",
                response_time=total_time,
                response_length=0,
                context={},
                exception=None,
            )
            print(f"Get key: {key}, result: {result}")
        except Exception as e:
            total_time = (time.perf_counter() - start_time) * 1000
            # 失敗イベントを発火
            self.user.environment.events.request.fire(
                request_type="Redis",
                name="get_value",
                response_time=total_time,
                response_length=0,
                context={},
                exception=e,
            )

class RedisUser(HttpUser):
    tasks = [RedisTaskSet]
    wait_time = between(1, 5)
    host = os.environ.get("REDIS_HOST", "localhost:7100")
