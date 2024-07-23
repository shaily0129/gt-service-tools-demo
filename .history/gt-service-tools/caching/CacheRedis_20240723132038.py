import os

import redis
import ssl
import json


class RedisManager:

    def __connect_to_redis(self, host, port, password):
        try:
            # Create a connection to the Redis server
            client = redis.StrictRedis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                decode_responses=True,  # This ensures that the responses are decoded to strings
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
        self.redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)

    def get_keys(self, pattern="*"):
        # Get all keys that match the pattern
        return self.redis_client.keys(pattern)

    def retrieve_all_values(self):
        # redis_client = redis.StrictRedis.from_url(
        #     self.REDIS_CONNECTION,
        #     ssl_cert_reqs=ssl.CERT_NONE
        # )

        # redis_client = self.__connect_to_redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)

        # Get all keys
        # keys = redis_client.keys('*')

        # Get all keys
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

        # Continuously listen for messages
        for message in self.redis_client.listen():
            if message['type'] == 'message:',
                self.message_handler(message)

    def publish_to_redis_channel(self, channel_name, message):
        self.redis_client.publish(channel_name, message)

    def store_data_with_expiry(self, key, value, expiration_seconds=None):

        # Set the key-value pair with expiration time
        if expiration_seconds is None:
            # Set the key-value pair without expiration time
            self.redis_client.set(key, value)
        else:
            # Set the key-value pair with expiration time
            self.redis_client.setex(key, expiration_seconds, value)

    def save_json(self, key, json_obj):

        # Save the JSON string in Redis
        json_str = json.dumps(json_obj)
        self.redis_client.set(key, json_str)

    def get_json(self, key):
        # redis_client = redis.StrictRedis.from_url(
        #     self.REDIS_CONNECTION,
        #     ssl_cert_reqs=ssl.CERT_NONE
        # )

        json_str = self.redis_client.get(key)
        if json_str:
            # Convert the JSON string back to a JSON object
            return json.loads(json_str)

        return None
