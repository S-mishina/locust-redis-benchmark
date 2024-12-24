import time
from redis.cluster import RedisCluster, ClusterNode, ClusterDownError

# 初期接続ノードを ClusterNode オブジェクトとして指定
startup_nodes = [
    ClusterNode("localhost", 7100)
]

def connect_to_redis_cluster():
    while True:
        try:
            # Redisクラスターに接続
            redis_cluster = RedisCluster(
                startup_nodes=startup_nodes,
                decode_responses=True,
                ssl=False,
                ssl_cert_reqs=None,
                socket_timeout=1,
            )
            print("Connected to Redis cluster")
            return redis_cluster
        except ClusterDownError:
            print("Cluster is down. Retrying...")
            time.sleep(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1)

def main():
    try:
        redis_cluster = connect_to_redis_cluster()
        # キーと値の操作
        redis_cluster.set("key1", "value1")
        value = redis_cluster.get("key1")
        print(f"Retrieved value for 'key1': {value}")
    except Exception as e:
        print(f"Error connecting to Redis Cluster: {e}")

if __name__ == "__main__":
    main()
