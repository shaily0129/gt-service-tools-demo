

# import os

# import redis
# import ssl
# import json


# class RedisManager:

#     def __connect_to_redis(self, host, port, password):
#         try:
#             # Create a connection to the Redis server
#             client = redis.StrictRedis(
#                 host=self.redis_host,
#                 port=self.redis_port,
#                 password=self.redis_password,
#                 decode_responses=True,  # This ensures that the responses are decoded to strings
#             )

#             # Test the connection
#             pong = client.ping()
#             if not pong:
#                 print("Failed to Connect to Redis!")

#             return client

#         except redis.ConnectionError as e:
#             print(f"Failed to connect to Redis: {e}")
#             return None

#     def __init__(self):
#         self.redis_host = os.getenv("redis_host")
#         self.redis_port = int(os.getenv("redis_host_port"))
#         self.redis_password = os.getenv("redis_host_password")

#     def retrieve_all_values(self):
#         # redis_client = redis.StrictRedis.from_url(
#         #     self.REDIS_CONNECTION,
#         #     ssl_cert_reqs=ssl.CERT_NONE
#         # )

#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         # Get all keys
#         keys = redis_client.keys("*")

#         # Get values associated with keys
#         values = redis_client.mget(keys)

#         # Create a dictionary to store key-value pairs
#         all_values = {}

#         # Zip keys and values together and add them to the dictionary
#         for key, value in zip(keys, values):
#             if value:
#                 value = value.decode("utf-8")
#             all_values[key.decode("utf-8")] = value

#         return all_values

#     def delete_all(self):

#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         redis_client.flushdb()

#     def message_handler(self, message):
#         print(f"TODO - Received message: {message['data'].decode('utf-8')}")

#     def subscribe_to_redis_channel(self, channel_name):
#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         redis_client.subscribe(channel_name)

#         # Continuously listen for messages
#         for message in redis_client.listen():
#             if message["type"] == "message":
#                 self.message_handler(message)

#     def publish_to_redis_channel(self, channel_name, message):

#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         redis_client.redis_client.publish(channel_name, message)

#     def store_data_with_expiry(self, key, value, expiration_seconds=None):

#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         # Set the key-value pair with expiration time
#         if expiration_seconds is None:
#             # Set the key-value pair without expiration time
#             redis_client.set(key, value)
#         else:
#             # Set the key-value pair with expiration time
#             redis_client.setex(key, expiration_seconds, value)

#     def retrieve_all_values(self):
#         # Connect to Redis server using the provided URI and disable SSL certificate verification
#         # redis_client = redis.StrictRedis.from_url(
#         #     self.REDIS_CONNECTION,
#         #     ssl_cert_reqs=ssl.CERT_NONE
#         # )
#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         # Get all keys
#         keys = redis_client.keys("*")

#         # Get values associated with keys
#         values = redis_client.mget(keys)

#         # Create a dictionary to store key-value pairs
#         all_values = {}

#         # Zip keys and values together and add them to the dictionary
#         # for key, value in zip(keys, values):
#         #     if value:
#         #         value = value.decode('utf-8')
#         #     all_values[key.decode('utf-8')] = value
#         for key, value in zip(keys, values):
#             all_values[key] = value

#         return all_values

#     def save_json(self, key, json_obj):
#         # redis_client = redis.StrictRedis.from_url(
#         #     self.REDIS_CONNECTION,
#         #     ssl_cert_reqs=ssl.CERT_NONE
#         # )
#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         t = type(json_obj)
#         # agent_response_json = json.dumps(json_obj, default=lambda o: o.__dict__)

#         # Save the JSON string in Redis
#         redis_client.set(key, json_obj)

#     def get_json(self, key):
#         # redis_client = redis.StrictRedis.from_url(
#         #     self.REDIS_CONNECTION,
#         #     ssl_cert_reqs=ssl.CERT_NONE
#         # )
#         redis_client = self.__connect_to_redis(
#             host=self.redis_host, port=self.redis_port, password=self.redis_password
#         )

#         json_str = redis_client.get(key)
#         if json_str:
#             # Convert the JSON string back to a JSON object
#             return json.loads(json_str)

#         return None


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
                decode_responses=True,  # This ensures that the responses are decoded to strings
            )

            # Test the connection
            if not client.ping():
                print("Failed to Connect to Redis!")
                return None

            return client

        except redis.ConnectionError as e:
            print(f"Failed to connect to Redis: {e}")
            return None

    def __init__(self):
        self.redis_host = os.getenv("redis_host")
        self.redis_port = int(os.getenv("redis_host_port"))
        self.redis_password = os.getenv("redis_host_password")
        self.redis_client = self.__connect_to_redis(
            host=self.redis_host, port=self.redis_port, password=self.redis_password
        )

    def retrieve_all_values(self):
        if self.redis_client is None:
            return {}

        # Get all keys
        keys = self.redis_client.keys("*")

        # Get values associated with keys
        values = self.redis_client.mget(keys)

        # Create a dictionary to store key-value pairs
        all_values = {key: value for key, value in zip(keys, values)}

        return all_values

    def delete_all(self):
        if self.redis_client is not None:
            self.redis_client.flushdb()

    def message_handler(self, message):
        print(f"TODO - Received message: {message['data']}")

    def subscribe_to_redis_channel(self, channel_name):
        if self.redis_client is None:
            return

        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(channel_name)

        # Continuously listen for messages
        for message in pubsub.listen():
            if message["type"] == "message":
                self.message_handler(message)

    def publish_to_redis_channel(self, channel_name, message):
        if self.redis_client is not None:
            self.redis_client.publish(channel_name, message)

    def store_data_with_expiry(self, key, value, expiration_seconds=None):
        if self.redis_client is None:
            return

        # Set the key-value pair with expiration time
        if expiration_seconds is None:
            # Set the key-value pair without expiration time
            self.redis_client.set(key, value)
        else:
            # Set the key-value pair with expiration time
            self.redis_client.setex(key, expiration_seconds, value)

    def save_json(self, key, json_obj):
        if self.redis_client is None:
            return

        # Save the JSON string in Redis
        json_str = json.dumps(json_obj)
        self.redis_client.set(key, json_str)

    def get_json(self, key):
        if self.redis_client is None:
            return None

        json_str = self.redis_client.get(key)
        if json_str:
            # Convert the JSON string back to a JSON object
            return json.loads(json_str)

        return None
