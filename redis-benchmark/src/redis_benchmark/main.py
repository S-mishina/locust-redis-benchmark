import argparse
import os
import sys
import gevent
from locust.env import Environment
from locust.runners import LocalRunner
from redis_benchmark.scenario import RedisUser
from locust.stats import stats_printer
from locust.log import setup_logging
setup_logging("DEBUG", None)  # デバッグログを有効化

def main():
    if os.environ.get("REDIS_HOST") is not None:
        print("REDIS_HOST is already set.")
        sys.exit(1)
    if os.environ.get("REDIS_PORT") is not None:
        print("REDIS_PORT is already set.")
        sys.exit(1)
    if os.environ.get("HIT_RATE") is not None:
        print("HIT_RATE is already set.")
        sys.exit(1)

    parser = argparse.ArgumentParser(
        description="A tool to perform load testing of Redis."
    )
    parser.add_argument(
        "--fqdn", "-f",
        type=str,
        required=False,
        default="localhost",
        help="Specify the hostname of the Redis server (default: localhost)."
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        required=False,
        default=6379,
        help="Specify the port of the Redis server (default: 6379)."
    )
    parser.add_argument(
        "--hit-rate", "-r",
        type=float,
        required=False,
        default=0.5,
        help="Specify the cache hit rate as a float between 0 and 1 (default: 0.5)."
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        required=False,
        default=60,
        help="Specify the duration of the test in seconds (default: 60)."
    )
    parser.add_argument(
        "--connections", "-c",
        type=int,
        required=False,
        default=1,
        help="Specify the number of concurrent connections (default: 1)."
    )
    parser.add_argument(
        "--requests", "-n",
        type=int,
        required=False,
        default=1000,
        help="Specify the number of requests to send (default: 1000)."
    )
    parser.parse_args()
    args = parser.parse_args()
    os.environ["REDIS_HOST"] = args.fqdn
    os.environ["REDIS_PORT"] = str(args.port)
    os.environ["HIT_RATE"] = str(args.hit_rate)
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

if __name__ == "__main__":
    main()
