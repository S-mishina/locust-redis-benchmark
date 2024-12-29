import argparse
import os
import sys
import gevent
from locust.env import Environment
from locust.runners import LocalRunner
from scenario import RedisUser
from utils import generate_string, init_redis_set, redis_connect
from locust.stats import stats_printer
import logging

logger = logging.getLogger(__name__)

def redis_load_test(args):
    os.environ["REDIS_HOST"] = args.fqdn
    os.environ["REDIS_PORT"] = str(args.port)
    os.environ["HIT_RATE"] = str(args.hit_rate)
    os.environ["VALUE_SIZE"] = str(args.value_size)
    os.environ["TTL"] = int(args.ttl)
    os.environ["CONNECTIONS_POOL"] = str(args.connections_pool)
    env = Environment(user_classes=[RedisUser])
    env.events.request.add_listener(lambda **kwargs: stats_printer(env.stats))
    runner = LocalRunner(env)
    RedisUser.host = f"http://{args.fqdn}:{args.port}"
    gevent.spawn(stats_printer(env.stats))
    runner.start(user_count=args.connections, spawn_rate=args.spawn_rate)
    stats_printer(env.stats)
    logger.info("Starting Locust load test...")
    gevent.sleep(args.duration)
    runner.quit()
    logger.info("Load test completed.")

def init_load_test(args):
    os.environ["REDIS_HOST"] = args.fqdn
    os.environ["REDIS_PORT"] = str(args.port)
    os.environ["HIT_RATE"] = str(args.hit_rate)
    os.environ["VALUE_SIZE"] = str(args.value_size)
    os.environ["TTL"] = int(args.ttl)
    redis_client = redis_connect()
    value = generate_string(args.value_size)
    init_redis_set(redis_client, value, os.environ["TTL"])

def add_common_arguments(parser):
    """
    common arguments for loadtest
    """
    group = parser.add_argument_group("Common Arguments")
    group.add_argument(
        "--fqdn", "-f",
        type=str,
        required=False,
        default="localhost",
        help="Specify the hostname of the Redis server (default: localhost)."
    )
    group.add_argument(
        "--port", "-p",
        type=int,
        required=False,
        default=6379,
        help="Specify the port of the Redis server (default: 6379)."
    )
    group.add_argument(
        "--hit-rate", "-r",
        type=float,
        required=False,
        default=0.5,
        help="Specify the cache hit rate as a float between 0 and 1 (default: 0.5)."
    )
    group.add_argument(
        "--duration", "-d",
        type=int,
        required=False,
        default=60,
        help="Specify the duration of the test in seconds (default: 60)."
    )
    group.add_argument(
        "--connections", "-c",
        type=int,
        required=False,
        default=1,
        help="Specify the number of concurrent connections (default: 1)."
    )
    group.add_argument(
        "--spawn_rate", "-n",
        type=int,
        required=False,
        default=1,
        help="Specify the number of requests to send (default: 1)."
    )
    group.add_argument(
        "--value-size", "-k",
        type=int,
        required=False,
        default=1,
        help="Specify the size of the keys in KB (default: 1)."
    )
    group.add_argument(
        "--ttl", "-t",
        type=int,
        required=False,
        default=60,
        help="Specify the time-to-live for the keys in seconds (default: 60)."
    )
    group.add_argument(
        "--connections-pool", "-l",
        type=int,
        required=False,
        default=1000000,
        help="Specify the number of connections in the pool (default: 1000000)."
    )
    group.add_argument(
        "--query-timeout", "-q",
        type=int,
        required=False,
        default=1,
        help="Specify the query timeout in seconds (default: 1)."
    )
    group.add_argument(
        "--set-keys", "-s",
        type=int,
        required=False,
        default=1000,
        help="Specify the number of keys to set in the cache (default: 1000). ※init redis only parameter"
    )
def main():
    parser = argparse.ArgumentParser(
        description="A tool to perform load testing of Redis and other systems."
    )
    subparsers = parser.add_subparsers(dest="command")

    loadtest_parser = subparsers.add_parser("loadtest", help="Load testing commands")
    loadtest_subparsers = loadtest_parser.add_subparsers(dest="subcommand")
    redis_parser = loadtest_subparsers.add_parser("redis", help="Run load test on Redis")
    add_common_arguments(redis_parser)
    redis_parser.set_defaults(func=redis_load_test)

    init_parser = subparsers.add_parser("init", help="Initialization commands")
    init_subparsers = init_parser.add_subparsers(dest="subcommand")
    init_redis_parser = init_subparsers.add_parser("redis", help="Initialize Redis")
    add_common_arguments(init_redis_parser)
    init_redis_parser.set_defaults(func=init_load_test)

    args = parser.parse_args()

    if args.command and args.subcommand:
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
