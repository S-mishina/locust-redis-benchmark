import os
import unittest
from unittest.mock import Mock
from cache_benchmark.utils import generate_string, init_cache_set, set_env_vars


class TestUtils(unittest.TestCase):
    def test_generate_string(self):
        result = generate_string(1)
        self.assertIsInstance(result, str)

    def test_set_env_vars(self):
        args = Mock()
        args.fqdn = "localhost"
        args.port = 6379
        args.hit_rate = 0.9
        args.value_size = 1024
        args.ttl = 60
        args.connections_pool = 10

        set_env_vars(args)

        self.assertEqual(os.environ["REDIS_HOST"], "localhost")
        self.assertEqual(os.environ["REDIS_PORT"], "6379")
        self.assertEqual(os.environ["HIT_RATE"], "0.9")
        self.assertEqual(os.environ["VALUE_SIZE"], "1024")
        self.assertEqual(os.environ["TTL"], "60")
        self.assertEqual(os.environ["CONNECTIONS_POOL"], "10")

    def test_init_cache_set(self):
        cache_client = Mock()
        value = "test_value"
        ttl = 60
        cache_client.get.return_value = None
        cache_client.set.return_value = True
        result = init_cache_set(cache_client, value, ttl)
        self.assertEqual(cache_client.set.call_count, 999)
        self.assertEqual(cache_client.get.call_count, 999)


if __name__ == "__main__":
    unittest.main()
