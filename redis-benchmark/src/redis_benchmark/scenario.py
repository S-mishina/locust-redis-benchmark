import hashlib
import os
import logging
from locust import HttpUser, TaskSet, task, between
from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
import random
import time

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed
from utils import generate_string

class RedisTaskSet(TaskSet):
    total_requests = 0
    cache_hits = 0
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type((TimeoutError, ConnectionError, ClusterDownError)),
    )
    def on_start(self):
        startup_nodes = [
            ClusterNode(os.environ.get("REDIS_HOST"), int(os.environ.get("REDIS_PORT")))
        ]
        try:
            self.redis_client = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=True,
                timeout=2,
                ssl=False,
                max_connections=1000000,
                ssl_cert_reqs=None,
            )

        except ClusterDownError as e:
            logging.warning(f"Cluster is down. Retrying...: {e}")
        except TimeoutError as e:
            logging.warning(f"Timeout error during Redis initialization: {e}")
        except Exception as e:
            logging.warning(f"Unexpected error during Redis initialization: {e}")

    def on_stop(self):
        if self.__class__.total_requests > 0:
            hit_rate = (self.__class__.cache_hits / self.__class__.total_requests) * 100
            logging.info(f"Total Requests: {self.__class__.total_requests}")
            logging.info(f"Cache Hits: {self.__class__.cache_hits}")
            logging.info(f"Cache Hit Rate: {hit_rate:.2f}%")
        else:
            logging.info("Total Requests: 0")
            logging.info("Cache Hit Rate: N/A")

    @task
    def cache_scenario(self):
        hit_rate = float(os.environ.get("HIT_RATE"))
        self.__class__.total_requests += 1
        if self.redis_client is None:
            logging.warning("Redis client is not initialized.")
            return
        total_time = 0
        if random.random() < float(hit_rate):
            try:
                key = f"key_{random.randint(1, 1000)}"
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
                    value = generate_string(os.environ.get("VALUE_SIZE"))
                    ttl = int(os.environ.get("TTL"))
                    result = self.redis_client.set(key, value, ex=int(ttl))
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
                logging.error(f"Error during cache miss: {e}")
        else:
            try:
                hash_key = hashlib.sha256(str(time.time_ns()).encode()).hexdigest()
                start_time = time.perf_counter()
                result = self.redis_client.get(hash_key)
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
                ttl = int(os.environ.get("TTL"))
                result = self.redis_client.set(hash_key, generate_string(os.environ.get("VALUE_SIZE")), ex=ttl)
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
                logging.error(f"Error during cache hit: {e}")

class RedisUser(HttpUser):
    tasks = [RedisTaskSet]
    wait_time = between(1, 1)
    host = os.environ.get("REDIS_HOST")
