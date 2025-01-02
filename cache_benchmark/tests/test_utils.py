import os
import unittest
from unittest.mock import Mock
from cache_benchmark.src.cache_benchmark.utils import generate_string, init_cache_set, set_env_vars

class TestUtils(unittest.TestCase):
    def test_generate_string(self):
        result = generate_string(1)  # 1KBの文字列を生成
        self.assertIsInstance(result, str)

if __name__ == "__main__":
    unittest.main()
