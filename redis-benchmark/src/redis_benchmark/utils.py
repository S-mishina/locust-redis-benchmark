
import time
from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
import os
import logging

def generate_string(size_in_kb):
    return "A" * (int(size_in_kb) * 1024)

def redis_connect():
    startup_nodes = [
        ClusterNode(os.environ.get("REDIS_HOST"), int(os.environ.get("REDIS_PORT")))
    ]
    try:
        conn = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            timeout=2,
            ssl=False,
            max_connections=int(os.environ.get("CONNECTIONS_POOL")),
            ssl_cert_reqs=None,
        )
    except ClusterDownError as e:
        logging.warning(f"Cluster is down. Retrying...: {e}")
        conn = None
    except TimeoutError as e:
        logging.warning(f"Timeout error during Redis initialization: {e}")
        conn = None
    except Exception as e:
        logging.warning(f"Unexpected error during Redis initialization: {e}")
        conn = None
    except ConnectionError as e:
        logging.warning(f"Connection error: {e}")
        conn = None
    return conn

def locust_redis_get(self, redis_connection, key, name):
    start_time = time.perf_counter()
    try:
        result = redis_connection.get(key)
        total_time = (time.perf_counter() - start_time) * 1000
        self.user.environment.events.request.fire(
            request_type="Redis",
            name="get_value_{}".format(name),
            response_time=total_time,
            response_length=0,
            context={},
            exception=None,
        )
    except Exception as e:
        total_time = (time.perf_counter() - start_time) * 1000
        self.user.environment.events.request.fire(
            request_type="Redis",
            name="get_value_{}".format(name),
            response_time=total_time,
            response_length=0,
            context={},
            exception=e,
        )
        logging.error(f"Error during cache hit: {e}")
    return result

def locust_redis_set(self, redis_connection, key , value , name, ttl):
    start_time = time.perf_counter()
    try:
        result = redis_connection(key, value, ex=int(ttl))
        total_time = (time.perf_counter() - start_time) * 1000
        self.user.environment.events.request.fire(
            request_type="Redis",
            name="set_value__{}".format(name),
            response_time=total_time,
            response_length=0,
            context={},
            exception=None,
        )
    except Exception as e:
        self.user.environment.events.request.fire(
            request_type="Redis",
            name="set_value__{}".format(name),
            response_time=total_time,
            response_length=0,
            context={},
            exception=e,
        )
        logging.error(f"Error during cache hit: {e}")
        return result
