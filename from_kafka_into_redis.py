import json
from datetime import datetime
from time import sleep

import redis
from kafka import KafkaConsumer
from rich.progress import track


KAFKA_TOPIC_NAME = "test"
KAFKA_CONSUMER = KafkaConsumer(
    bootstrap_servers=["localhost:9092"],
    auto_offset_reset="earliest",
    value_deserializer=json.loads,
)
REDIS_CONN = redis.Redis(host="localhost", port=6379, password="password")
REDIS_KEY_EXPIRY_TIME_SEC = 3600 * 24 * 7

KAFKA_CONSUMER.subscribe(KAFKA_TOPIC_NAME)
for data in track(KAFKA_CONSUMER, description="Reading from Kafka into Redis..."):
    datetime_obj = datetime.fromtimestamp(data.timestamp // 1000)  # Kafka timestamp is in ms
    key = f"{datetime_obj.day}/{datetime_obj.hour}"
    data_values = data.value
    data_values["timestamp"] = datetime_obj.timestamp()

    REDIS_CONN.incr(name=key)
    REDIS_CONN.expire(name=key, time=REDIS_KEY_EXPIRY_TIME_SEC, nx=True)

    REDIS_CONN.rpush(f"{key}/details", json.dumps(data_values))
    REDIS_CONN.expire(name=f"{key}/details", time=3600 * 7, nx=True)

    REDIS_CONN.rpush("1000_latest_trips", json.dumps(data_values))
    REDIS_CONN.ltrim(name="1000_latest_trips", start=-1000, end=-1)
