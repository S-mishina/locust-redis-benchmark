from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
from redis.exceptions import TimeoutError, ConnectionError
from valkey.cluster import ValkeyCluster as ValkeyCluster, ClusterNode as ValleyClusterNode, ClusterDownError as ValkeyClusterDownError
from valkey.exceptions import ConnectionError as ValkeyConnectionError, TimeoutError as ValkeyTimeoutError
from distutils.util import strtobool
import os
import logging

class CacheConnect:
    def redis_connect(self):
        """
        Initializes a connection to the Redis cluster.
        
        Returns:
            RedisCluster: Redis cluster connection object.
        """
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")
        connections_pool = os.environ.get("CONNECTIONS_POOL")
        ssl = os.environ.get("SSL")
        query_timeout = os.environ.get("QUERY_TIMEOUT")
        logging.info(redis_host)
        logging.info(redis_port)
        logging.info(connections_pool)
        logging.info(ssl)
        logging.info(f"Connecting to Redis cluster at {redis_host}:{redis_port} with {connections_pool} connections SSL={ssl}.")

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
                timeout=query_timeout,
                ssl=bool(strtobool(ssl)),
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

    def valkey_connect(self):
        """
        Initializes a connection to the Valley cluster.

        Returns:
            ValkeyCluster: Valley cluster connection object.
        """
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")
        connections_pool = os.environ.get("CONNECTIONS_POOL")
        ssl = os.environ.get("SSL")
        query_timeout = os.environ.get("QUERY_TIMEOUT")
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
                timeout=query_timeout,
                ssl=bool(strtobool(ssl)),
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
