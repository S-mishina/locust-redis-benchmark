import os
from unittest.mock import patch, Mock
import unittest
from cache_benchmark.src.cache_benchmark.cash_connect import *

class TestCashConnect(unittest.TestCase):
    def setUp(self):
        os.environ.clear()  # 既存の環境変数をクリア
        os.environ["REDIS_HOST"] = "localhost"
        os.environ["REDIS_PORT"] = "6379"
        os.environ["CONNECTIONS_POOL"] = "10"

    def tearDown(self):
        os.environ.clear()  # 既存の環境変数をクリア

    def test_redis_connect_missing_env_vars(self):
        self.tearDown()  # Ensure environment variables are not set
        conn = CacheConnect.redis_connect()
        self.assertIsNone(conn)

    def test_redis_connect_cluster_down_error(self):
        with patch("redis.cluster.RedisCluster", side_effect=ClusterDownError):
            conn = CacheConnect.redis_connect()
            self.assertIsNone(conn)

    def test_redis_connect_timeout_error(self):
        with patch("redis.cluster.RedisCluster", side_effect=TimeoutError):
            conn = CacheConnect.redis_connect()
            self.assertIsNone(conn)

    def test_redis_connect_connection_error(self):
        with patch("redis.cluster.RedisCluster", side_effect=ConnectionError):
            conn = CacheConnect.redis_connect()
            self.assertIsNone(conn)

    def test_redis_connect_unexpected_error(self):
        with patch("redis.cluster.RedisCluster", side_effect=Exception):
            conn = CacheConnect.redis_connect()
            self.assertIsNone(conn)

    def test_valkey_connect_missing_env_vars(self):
        self.tearDown()  # Ensure environment variables are not set
        conn = CacheConnect.valkey_connect()
        self.assertIsNone(conn)

    def test_valkey_connect_cluster_down_error(self):
        with patch("valkey.cluster.ValkeyCluster", side_effect=ValkeyClusterDownError):
            conn = CacheConnect.valkey_connect()
            self.assertIsNone(conn)

    def test_valkey_connect_timeout_error(self):
        with patch("valkey.cluster.ValkeyCluster", side_effect=ValkeyTimeoutError):
            conn = CacheConnect.valkey_connect()
            self.assertIsNone(conn)

    def test_valkey_connect_connection_error(self):
        with patch("valkey.cluster.ValkeyCluster", side_effect=ValkeyConnectionError):
            conn = CacheConnect.valkey_connect()
            self.assertIsNone(conn)

    def test_valkey_connect_unexpected_error(self):
        with patch("valkey.cluster.ValkeyCluster", side_effect=Exception):
            conn = CacheConnect.valkey_connect()
            self.assertIsNone(conn)
