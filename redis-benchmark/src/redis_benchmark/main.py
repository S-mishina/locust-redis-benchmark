import argparse
import os
import sys
import gevent
from locust.env import Environment
from locust.runners import LocalRunner
from scenario import RedisUser
from utils import generate_string
from redis.cluster import RedisCluster, ClusterDownError, ClusterNode
from locust.stats import stats_printer
from locust.log import setup_logging
import random

setup_logging("DEBUG", None)

def redis_load_test(args):
    os.environ["REDIS_HOST"] = args.fqdn
    os.environ["REDIS_PORT"] = str(args.port)
    os.environ["HIT_RATE"] = str(args.hit_rate)
    os.environ["VALUE_SIZE"] = str(args.value_size)
    os.environ["TTL"] = str(args.ttl)
    env = Environment(user_classes=[RedisUser])
    env.events.request.add_listener(lambda **kwargs: stats_printer(env.stats))
    runner = LocalRunner(env)
    RedisUser.host = f"http://{args.fqdn}:{args.port}"
    gevent.spawn(stats_printer(env.stats))
    runner.start(user_count=args.connections, spawn_rate=args.requests)
    stats_printer(env.stats)
    print("Starting Locust load test...")
    gevent.sleep(args.duration)
    runner.quit()
    print("Load test completed.")

def init_load_test(args):
    os.environ["REDIS_HOST"] = args.fqdn
    os.environ["REDIS_PORT"] = str(args.port)
    os.environ["HIT_RATE"] = str(args.hit_rate)
    os.environ["VALUE_SIZE"] = str(args.value_size)
    os.environ["TTL"] = str(args.ttl)
    startup_nodes = [
        ClusterNode(os.environ.get("REDIS_HOST"), os.environ.get("REDIS_PORT"))
    ]
    try:
        redis_client = RedisCluster(
            startup_nodes=startup_nodes,
            decode_responses=True,
            ssl=False,
            ssl_cert_reqs=None,
            socket_timeout=1
        )
    except ClusterDownError:
        print("Cluster is down. Retrying...")
        redis_client = None
    except Exception as e:
        print(f"Unexpected error during Redis initialization: {e}")
        redis_client = None
    if redis_client is not None:
        print("Redis client initialized successfully.")
        print("Populating cache with 10,000 keys...")
        for i in range(1, 10000):
            key = f"key_{random.randint(1, 10000)}"
            redis_client.set(key, generate_string(os.environ.get("VALUE_SIZE")), ex=int(os.environ.get("TTL")))
        print("Success")
    else:
        print("Redis client initialization failed.")
        exit(1)

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
        "--requests", "-n",
        type=int,
        required=False,
        default=1000,
        help="Specify the number of requests to send (default: 1000)."
    )
    group.add_argument(
        "--value-size", "-k",
        type=int,
        required=False,
        default=1,
        help="Specify the size of the keys in MB (default: 1)."
    )
    group.add_argument(
        "--ttl", "-t",
        type=int,
        required=False,
        default=60,
        help="Specify the time-to-live for the keys in seconds (default: 60)."
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
