import csv
from cash_connect import*
import logging
import gevent
from locust.env import Environment
from locust.runners import LocalRunner
from scenario import RedisUser
import locust
from locust.stats import stats_printer

logger = logging.getLogger(__name__)

def generate_string(size_in_kb):
    """
    Generates a string of a given size in kilobytes.
    
    Args:
        size_in_kb (int): Size of the string in kilobytes.
    
    Returns:
        str: Generated string.
    """
    return "A" * (int(size_in_kb) * 1024)

def init_cache_set(cache_client, value, ttl):
    """
    Initializes the Redis cache with a set of keys.

    Args:
        cache_client (RedisCluster): Redis cluster connection object.
        value (str): Value to set in Redis.
        ttl (int): Time-to-live for the keys in seconds.
    """
    if cache_client is not None:
        logging.info("Redis client initialized successfully.")
        logging.info("Populating cache with 1,000 keys...")
        for i in range(1, 1000):
            key = f"key_{i}"
            if cache_client.get(key) is None:
                cache_client.set(key, value, ex=int(ttl))
        logging.info("Success")
    else:
        logging.error("Cache client initialization failed.")
        exit(1)

def save_results_to_csv(stats, filename="test_results.csv"):
    """
    Saves the test results to a CSV file.

    Args:
        stats (Stats): Locust stats object.
        filename (str): Name of the CSV file to save the results to.
    """
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Request Name", "Total Requests", "Failures", "Average Response Time",
                         "Min Response Time", "Max Response Time", "RPS"])
        for name, entry in stats.entries.items():
            writer.writerow([
                name,
                entry.num_requests,
                entry.num_failures,
                entry.avg_response_time,
                entry.min_response_time,
                entry.max_response_time,
                entry.current_rps
            ])

def set_env_vars(args):
    """
    Sets the environment variables for the test.

    Args:
        args (Namespace): Command-line arguments.
    """
    os.environ["REDIS_HOST"] = args.fqdn
    os.environ["REDIS_PORT"] = str(args.port)
    os.environ["HIT_RATE"] = str(args.hit_rate)
    os.environ["VALUE_SIZE"] = str(args.value_size)
    os.environ["TTL"] = str(args.ttl)
    os.environ["CONNECTIONS_POOL"] = str(args.connections_pool)

def locust_runner_cash_benchmark():
    env = Environment(user_classes=[RedisUser])
    env.events.request.add_listener(lambda **kwargs: stats_printer(env.stats))
    runner = LocalRunner(env)
    RedisUser.host = f"http://{args.fqdn}:{args.port}"
    gevent.spawn(stats_printer(env.stats))
    locust.events.init.fire(environment=env,cache_type="valkey_cluster")
    runner.start(user_count=args.connections, spawn_rate=args.spawn_rate)
    stats_printer(env.stats)
    logger.info("Starting Locust load test...")
    gevent.sleep(args.duration)
    runner.quit()
    logger.info("Load test completed.")
    save_results_to_csv(env.stats, filename="redis_test_results.csv")

