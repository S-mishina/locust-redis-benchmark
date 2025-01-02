import unittest
from unittest.mock import patch, MagicMock
import sys
from cache_benchmark.src.cache_benchmark.main import main, redis_load_test, valkey_load_test, init_redis_load_test, init_valkey_load_test
from cache_benchmark.src.cache_benchmark.scenario import RedisUser

class TestMain(unittest.TestCase):

    @patch('cache_benchmark.src.cache_benchmark.main.set_env_vars')
    @patch('cache_benchmark.src.cache_benchmark.main.locust_runner_cash_benchmark')
    def test_redis_load_test(self, mock_locust_runner, mock_set_env_vars):
        '''
        Test redis_load_test function

        This test case will check if the redis_load_test function calls set_env_vars and locust_runner_cash_benchmark functions with the correct arguments.

        Parameters:
        mock_locust_runner (MagicMock): Mock object for locust_runner_cash_benchmark function
        mock_set_env_vars (MagicMock): Mock object for set_env_vars function
        '''
        args = MagicMock()
        redis_load_test(args)
        mock_set_env_vars.assert_called_once_with(args)
        mock_locust_runner.assert_called_once_with(args, RedisUser)

    @patch('cache_benchmark.src.cache_benchmark.main.set_env_vars')
    @patch('cache_benchmark.src.cache_benchmark.main.locust_runner_cash_benchmark')
    def test_valkey_load_test(self, mock_locust_runner, mock_set_env_vars):
        '''
        Test valkey_load_test function

        This test case will check if the valkey_load_test function calls set_env_vars and locust_runner_cash_benchmark functions with the correct arguments.

        Parameters:
        mock_locust_runner (MagicMock): Mock object for locust_runner_cash_benchmark function
        mock_set_env_vars (MagicMock): Mock object for set_env_vars function
        '''
        args = MagicMock()
        valkey_load_test(args)
        mock_set_env_vars.assert_called_once_with(args)
        mock_locust_runner.assert_called_once_with(args, RedisUser)

    @patch('cache_benchmark.src.cache_benchmark.main.set_env_vars')
    @patch('cache_benchmark.src.cache_benchmark.main.CacheConnect.valkey_connect')
    @patch('cache_benchmark.src.cache_benchmark.main.generate_string')
    @patch('cache_benchmark.src.cache_benchmark.main.init_cache_set')
    @patch.dict('os.environ', {'TTL': '60'})
    def test_init_valkey_load_test_success(self, mock_init_cache_set, mock_generate_string, mock_valkey_connect, mock_set_env_vars):
        '''
        Test init_valkey_load_test function

        This test case will check if the init_valkey_load_test function calls set_env_vars, valkey_connect, generate_string, and init_cache_set functions with the correct arguments.

        Parameters:
        mock_init_cache_set (MagicMock): Mock object for init_cache_set function
        mock_generate_string (MagicMock): Mock object for generate_string function
        mock_valkey_connect (MagicMock): Mock object for valkey_connect function
        mock_set_env_vars (MagicMock): Mock object for set_env_vars function
        '''
        args = MagicMock()
        mock_valkey_connect.return_value = MagicMock()
        mock_generate_string.return_value = "test_value"
        init_valkey_load_test(args)
        mock_set_env_vars.assert_called_once_with(args)
        mock_valkey_connect.assert_called_once()
        mock_generate_string.assert_called_once_with(args.value_size)
        mock_init_cache_set.assert_called_once_with(mock_valkey_connect.return_value, "test_value", 60)

    @patch('cache_benchmark.src.cache_benchmark.main.set_env_vars')
    @patch('cache_benchmark.src.cache_benchmark.main.CacheConnect.redis_connect')
    @patch('cache_benchmark.src.cache_benchmark.main.generate_string')
    @patch('cache_benchmark.src.cache_benchmark.main.init_cache_set')
    @patch.dict('os.environ', {'TTL': '60'})
    def test_init_redis_load_test_success(self, mock_init_cache_set, mock_generate_string, mock_redis_connect, mock_set_env_vars):
        '''
        Test init_redis_load_test function

        This test case will check if the init_redis_load_test function calls set_env_vars, redis_connect, generate_string, and init_cache_set functions with the correct arguments.

        Parameters:
        mock_init_cache_set (MagicMock): Mock object for init_cache_set function
        mock_generate_string (MagicMock): Mock object for generate_string function
        mock_redis_connect (MagicMock): Mock object for redis_connect function
        mock_set_env_vars (MagicMock): Mock object for set_env_vars function
        '''
        args = MagicMock()
        mock_redis_connect.return_value = MagicMock()
        mock_generate_string.return_value = "test_value"
        init_redis_load_test(args)
        mock_set_env_vars.assert_called_once_with(args)
        mock_redis_connect.assert_called_once()
        mock_generate_string.assert_called_once_with(args.value_size)
        mock_init_cache_set.assert_called_once_with(mock_redis_connect.return_value, "test_value", 60)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('cache_benchmark.src.cache_benchmark.main.sys.exit')
    def test_main_no_args(self, mock_exit, mock_parse_args):
        '''
        Test main function with no arguments

        This test case will check if the main function calls sys.exit with the correct exit code when no arguments are provided.

        Parameters:
        mock_exit (MagicMock): Mock object for sys.exit function
        mock_parse_args (MagicMock): Mock object for argparse.ArgumentParser.parse_args function
        '''

        mock_parse_args.return_value = MagicMock(command=None, subcommand=None)
        main()
        mock_exit.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()
