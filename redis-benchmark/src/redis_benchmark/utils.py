import csv
import time
from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
from redis.exceptions import TimeoutError, ConnectionError
from valkey.cluster import ValkeyCluster as ValkeyCluster, ClusterNode as ValleyClusterNode, ClusterDownError as ValkeyClusterDownError
from valkey.exceptions import ConnectionError as ValkeyConnectionError, TimeoutError as ValkeyTimeoutError
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
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    connections_pool = os.environ.get("CONNECTIONS_POOL")
    logging.info(f"Connecting to Redis cluster at {redis_host}:{redis_port} with {connections_pool} connections.")

    if not redis_host or not redis_port or not connections_pool:
        logging.error("Environment variables REDIS_HOST, REDIS_PORT, and CONNECTIONS_POOL must be set.")
        return None

    startup_nodes = [
        ClusterNode(redis_host, int(redis_port))
    ]
    try:
        conn = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            timeout=2,
            ssl=False,
            max_connections=int(connections_pool),
            ssl_cert_reqs=None,
        )
    except ClusterDownError as e:
        logging.warning(f"Cluster is down. Retrying...: {e}")
        conn = None
    except TimeoutError as e:
        logging.warning(f"Timeout error during Redis initialization: {e}")
        conn = None
    except ConnectionError as e:
        logging.warning(f"Connection error: {e}")
        conn = None
    except Exception as e:
        logging.warning(f"Unexpected error during Redis initialization: {e}")
        conn = None
    return conn

def valkey_connect():
    """
    Initializes a connection to the Valley cluster.

    Returns:
        ValkeyCluster: Valley cluster connection object.
    """
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = os.environ.get("REDIS_PORT")
    connections_pool = os.environ.get("CONNECTIONS_POOL")
    logging.info(f"Connecting to Valley cluster at {redis_host}:{redis_port} with {connections_pool} connections.")
    if not redis_host or not redis_port or not connections_pool:
        logging.error("Environment variables REDIS_HOST, REDIS_PORT, and CONNECTIONS_POOL must be set.")
        return None
    startup_nodes = [
        ValleyClusterNode(redis_host, int(redis_port))
    ]
    try:
        conn = ValkeyCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            timeout=2,
            ssl=False,
            max_connections=int(connections_pool),
            ssl_cert_reqs=None,
        )
    except ValkeyClusterDownError as e:
        logging.warning(f"Cluster is down. Retrying...: {e}")
        conn = None
    except ValkeyTimeoutError as e:
        logging.warning(f"Timeout error during Valley initialization: {e}")
        conn = None
    except ValkeyConnectionError as e:
        logging.warning(f"Connection error: {e}")
        conn = None
    except Exception as e:
        logging.warning(f"Unexpected error during Valley initialization: {e}")
        conn = None
    return conn

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((TimeoutError, ConnectionError, ClusterDownError)),
)
def locust_redis_get(self, cache_connection, key, name):
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
        result = cache_connection.get(key)
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
def locust_redis_set(self, cache_connection, key, value, name, ttl):
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
        result = cache_connection.set(key, value, ex=int(ttl))
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

def save_results_to_csv(stats, filename="test_results.csv"):
    """
    Saves the test results to a CSV file.

    Args:
        stats (Stats): Locust stats object.
        filename (str): Name of the CSV file to save the results to.
    """
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Request Name", "Total Requests", "Failures", "Average Response Time",
                         "Min Response Time", "Max Response Time", "RPS"])
        for name, entry in stats.entries.items():
            writer.writerow([
                name,
                entry.num_requests,
                entry.num_failures,
                entry.avg_response_time,
                entry.min_response_time,
                entry.max_response_time,
                entry.current_rps
            ])
