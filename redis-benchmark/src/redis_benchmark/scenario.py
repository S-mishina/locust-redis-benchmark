import os
import time
from locust import HttpUser, TaskSet, task, between
from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
import random
import hashlib
import time


class RedisTaskSet(TaskSet):
    total_requests = 0
    cache_hits = 0
    def on_start(self):
        startup_nodes = [
            ClusterNode(os.environ.get("REDIS_HOST"), os.environ.get("REDIS_PORT"))
        ]
        try:
            self.redis_client = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=True,
                ssl=False,
                ssl_cert_reqs=None,
                socket_timeout=1
            )
        except ClusterDownError:
            print("Cluster is down. Retrying...")
            self.redis_client = None
        except Exception as e:
            print(f"Unexpected error during Redis initialization: {e}")
            self.redis_client = None
        print("Populating cache with 10,000 keys...")
        for i in range(1, 10000):
            key = f"key_{random.randint(1, 10000)}"
            value = f"value_{i}"
            self.redis_client.set(key, value)
    def on_stop(self):
        hit_rate = (self.__class__.cache_hits / self.__class__.total_requests) * 100
        print(f"Total Requests: {self.__class__.total_requests}")
        print(f"Cache Hits: {self.__class__.cache_hits}")
        print(f"Cache Hit Rate: {hit_rate:.2f}%")

    @task
    def cache_scenario(self):
        hit_rate = os.environ.get("HIT_RATE")
        self.__class__.total_requests += 1
        if random.random() < float(hit_rate):
            try:
                key = f"key_{random.randint(1, 10000)}"
                start_time = time.perf_counter()
                result = self.redis_client.get(key)
                total_time = (time.perf_counter() - start_time) * 1000
                self.user.environment.events.request.fire(
                    request_type="Redis",
                    name="get_value",
                    response_time=total_time,
                    response_length=0,
                    context={},
                    exception=None,
                )
                if result is None:
                    value = f"value_{random.randint(1, 10000)}"
                    result = self.redis_client.set(key, value)
                    self.user.environment.events.request.fire(
                        request_type="Redis",
                        name="set_value",
                        response_time=total_time,
                        response_length=0,
                        context={},
                        exception=None,
                    )
                else:
                    self.__class__.cache_hits += 1
            except Exception as e:
                self.user.environment.events.request.fire(
                    request_type="Redis",
                    name="get_value",
                    response_time=total_time,
                    response_length=0,
                    context={},
                    exception=e,
                )
        else:
            hash_value = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
            value = f"value_{random.randint(1, 10000)}"
            try:
                start_time = time.perf_counter()
                result = self.redis_client.get(hash_value)
                total_time = (time.perf_counter() - start_time) * 1000
                self.user.environment.events.request.fire(
                    request_type="Redis",
                    name="get_value",
                    response_time=total_time,
                    response_length=0,
                    context={},
                    exception=None,
                )
                start_time = time.perf_counter()
                result = self.redis_client.set(hash_value, value)
                total_time = (time.perf_counter() - start_time) * 1000
                self.user.environment.events.request.fire(
                    request_type="Redis",
                    name="set_value",
                    response_time=total_time,
                    response_length=0,
                    context={},
                    exception=None,
                )
            except Exception as e:
                total_time = (time.perf_counter() - start_time) * 1000
                self.user.environment.events.request.fire(
                    request_type="Redis",
                    name="set_value",
                    response_time=total_time,
                    response_length=0,
                    context={},
                    exception=e,
                )

class RedisUser(HttpUser):
    tasks = [RedisTaskSet]
    wait_time = between(1, 1)
    host = os.environ.get("REDIS_HOST")
