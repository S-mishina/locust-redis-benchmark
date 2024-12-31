import argparse
import os
import sys
from utils import *
from args import *
from cash_connect import*
from locust.stats import stats_printer
import locust
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@locust.events.init.add_listener
def on_locust_init(environment, **kwargs):
    if kwargs.get('cache_type'):
        if kwargs.get('cache_type') == "redis_cluster":
            logger.info("Locust environment redis_conn initialized.")
            environment.cache_conn = redis_connect()
        elif kwargs.get('cache_type') == "valkey_cluster":
            logger.info("Locust environment valkey_conn initialized.")
            environment.cache_conn = valkey_connect()


def redis_load_test(args):
    set_env_vars(args)
    locust_runner_cash_benchmark(args)

def valkey_load_test(args):
    set_env_vars(args)
    locust_runner_cash_benchmark(args)

def init_valkey_load_test(args):
    set_env_vars(args)
    cache_client = valkey_connect()
    if cache_client is None:
        logger.error("Redis client initialization failed.")
        sys.exit(1)
    value = generate_string(args.value_size)
    init_cache_set(cache_client, value, int(os.environ["TTL"]))

def init_redis_load_test(args):
    set_env_vars(args)
    cache_client = redis_connect()
    if cache_client is None:
        logger.error("Redis client initialization failed.")
        sys.exit(1)
    value = generate_string(args.value_size)
    init_cache_set(cache_client, value, int(os.environ["TTL"]))

def main():
    parser = argparse.ArgumentParser(
        description="A tool to perform load testing of Redis and other systems."
    )
    subparsers = parser.add_subparsers(dest="command")
    # loadtest subcommand
    loadtest_parser = subparsers.add_parser("loadtest", help="Load testing commands")
    loadtest_subparsers = loadtest_parser.add_subparsers(dest="subcommand")
    # loadtest redis subcommand
    redis_parser = loadtest_subparsers.add_parser("redis", help="Run load test on Redis")
    add_common_arguments(redis_parser)
    redis_parser.set_defaults(func=redis_load_test)
    # loadtest valkey subcommand
    valkey_parser = loadtest_subparsers.add_parser("valkey", help="Run load test on valkey")
    add_common_arguments(valkey_parser)
    redis_parser.set_defaults(func=valkey_load_test)
    # init subcommand
    init_parser = subparsers.add_parser("init", help="Initialization commands")
    init_subparsers = init_parser.add_subparsers(dest="subcommand")
    # init redis subcommand
    init_redis_parser = init_subparsers.add_parser("redis", help="Initialize Redis")
    add_common_arguments(init_redis_parser)
    init_redis_parser.set_defaults(func=init_redis_load_test)
    # init valkey subcommand
    init_valkey_parser = init_subparsers.add_parser("valkey", help="Initialize valkey")
    add_common_arguments(init_valkey_parser)
    init_valkey_parser.set_defaults(func=init_valkey_load_test)

    args = parser.parse_args()

    if args.command and args.subcommand:
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
