import os
import redis
import json

class RedisManager:

    def __connect_to_redis(self, host, port, password):
        try:
            # Create a connection to the Redis server
            client = redis.StrictRedis(
                host=host,
                port=port,
                password=password,
                decode_responses=True  # This ensures that the responses are decoded to strings
            )

            # Test the connection
            pong = client.ping()
            if not pong:
                print("Failed to Connect to Redis!")

            return client

        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            return None

    def __init__(self):
        self.redis_host = os.getenv("redis_host")
        self.redis_port = int(os.getenv("redis_host_port"))
        self.redis_password = os.getenv("redis_host_password")

    def get_keys(self, pattern="*"):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        return redis_client.keys(pattern)

    def retrieve_all_values(self):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        keys = redis_client.keys('*')
        values = redis_client.mget(keys)
        all_values = {}
        for key, value in zip(keys, values):
            all_values[key] = value
        return all_values

    def delete_all(self):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        redis_client.flushdb()

    def message_handler(self, message):
        print(f"TODO - Received message: {message['data']}")

    def subscribe_to_redis_channel(self, channel_name):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        redis_client.subscribe(channel_name)
        for message in redis_client.listen():
            if message['type'] == 'message':
                self.message_handler(message)

    def publish_to_redis_channel(self, channel_name, message):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        redis_client.publish(channel_name, message)

    def store_data_with_expiry(self, key, value, expiration_seconds=None):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        if expiration_seconds is None:
            redis_client.set(key, value)
        else:
            redis_client.setex(key, expiration_seconds, value)

    def save_json(self, key, json_obj):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        redis_client.set(key, json.dumps(json_obj))

    def get_json(self, key):
        redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
        json_str = redis_client.get(key)
        if json_str:
            return json.loads(json_str)
        return None
