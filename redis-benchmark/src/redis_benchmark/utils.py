import time
from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
from redis.exceptions import TimeoutError, ConnectionError
import os
import logging
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

def generate_string(size_in_kb):
    """
    Generates a string of a given size in kilobytes.
    
    Args:
        size_in_kb (int): Size of the string in kilobytes.
    
    Returns:
        str: Generated string.
    """
    return "A" * (int(size_in_kb) * 1024)

def redis_connect():
    """
    Initializes a connection to the Redis cluster.
    
    Returns:
        RedisCluster: Redis cluster connection object.
    """
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

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((TimeoutError, ConnectionError, ClusterDownError)),
)
def locust_redis_get(self, redis_connection, key, name):
    """
    Performs a GET operation on the Redis cluster with retry logic.
    
    Args:
        self: Locust task instance.
        redis_connection (RedisCluster): Redis cluster connection object.
        key (str): Key to get from Redis.
        name (str): Name for the request event.
    
    Returns:
        str: Value from Redis.
    """
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
        result = None
    return result

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((TimeoutError, ConnectionError, ClusterDownError)),
)
def locust_redis_set(self, redis_connection, key, value, name, ttl):
    """
    Performs a SET operation on the Redis cluster with retry logic.
    
    Args:
        self: Locust task instance.
        redis_connection (RedisCluster): Redis cluster connection object.
        key (str): Key to set in Redis.
        value (str): Value to set in Redis.
        name (str): Name for the request event.
        ttl (int): Time-to-live for the key in seconds.
    
    Returns:
        bool: True if the operation was successful, False otherwise.
    """
    start_time = time.perf_counter()
    try:
        result = redis_connection.set(key, value, ex=int(ttl))
        total_time = (time.perf_counter() - start_time) * 1000
        self.user.environment.events.request.fire(
            request_type="Redis",
            name="set_value_{}".format(name),
            response_time=total_time,
            response_length=0,
            context={},
            exception=None,
        )
    except Exception as e:
        total_time = (time.perf_counter() - start_time) * 1000
        self.user.environment.events.request.fire(
            request_type="Redis",
            name="set_value_{}".format(name),
            response_time=total_time,
            response_length=0,
            context={},
            exception=e,
        )
        logging.error(f"Error during cache set: {e}")
        result = None
    return result

def init_redis_set(redis_client, value, ttl):
    """
    Initializes the Redis cache with a set of keys.
    
    Args:
        redis_client (RedisCluster): Redis cluster connection object.
        value (str): Value to set in Redis.
        ttl (int): Time-to-live for the keys in seconds.
    """
    if redis_client is not None:
        logging.info("Redis client initialized successfully.")
        logging.info("Populating cache with 1,000 keys...")
        for i in range(1, 1000):
            key = f"key_{i}"
            if redis_client.get(key) is None:
                redis_client.set(key, value, ex=int(ttl))
        logging.info("Success")
    else:
        logging.error("Redis client initialization failed.")
        exit(1)
