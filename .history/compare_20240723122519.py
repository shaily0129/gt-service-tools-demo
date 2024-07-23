import os
import redis
import json

class RedisManager:
    def __connect_to_redis(self, host, port, password):
        try:
            client = redis.StrictRedis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True
            )
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
        self.redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)

    def get_keys(self, pattern="*"):
        return self.redis_client.keys(pattern)

    def retrieve_all_values(self):
        keys = self.redis_client.keys('*')
        values = self.redis_client.mget(keys)
        all_values = {key: value for key, value in zip(keys, values)}
        return all_values

    def delete_all(self):
        self.redis_client.flushdb()

    def message_handler(self, message):
        print(f"TODO - Received message: {message['data']}")

    def subscribe_to_redis_channel(self, channel_name):
        self.redis_client.subscribe(channel_name)
        for message in self.redis_client.listen():
            if message['type'] == 'message':
                self.message_handler(message)

    def publish_to_redis_channel(self, channel_name, message):
        self.redis_client.publish(channel_name, message)

    def store_data_with_expiry(self, key, value, expiration_seconds=None):
        if expiration_seconds is None:
            self.redis_client.set(key, value)
        else:
            self.redis_client.setex(key, expiration_seconds, value)

    def save_json(self, key, json_obj):
        json_str = json.dumps(json_obj)
        self.redis_client.set(key, json_str)

    def get_json(self, key):
        json_str = self.redis_client.get(key)
        if json_str:
            return json.loads(json_str)
        return None
