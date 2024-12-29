
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
