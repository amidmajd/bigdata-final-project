import csv
import json
import uuid
from datetime import datetime
from time import sleep

from kafka import KafkaProducer
from rich.progress import track

KAFKA_TOPIC_NAME = "test"
KAFKA_PRODUCER = KafkaProducer(
    bootstrap_servers="localhost:9092",
    key_serializer=str.encode,
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)


def send_data_to_kafka(header: list, data: list, key: str = uuid.uuid4().hex, timestamp=None):
    if timestamp:
        timestamp = int(timestamp) * 1000

    KAFKA_PRODUCER.send(
        KAFKA_TOPIC_NAME, key=key, value=dict(zip(header, data)), timestamp_ms=timestamp
    )


def send_real_data_to_kafka():
    with open("data.csv", newline="") as csv_file:
        data = csv.reader(csv_file, delimiter=",", quotechar="|")
        header = next(data)[1:]

        for row in track(data, description="Sending Data to Kafka..."):
            timestamp = datetime.strptime(row[0], "%m/%d/%Y %H:%M:%S").timestamp()
            row = row[1:]
            send_data_to_kafka(header=header, data=row, timestamp=timestamp)
            sleep(0.5)


def send_fake_data_to_kafka(n: int = 20, time_step: int = 1):
    header = ["Lat", "Lon", "Base"]
    for i in track(range(n), description="Sending Data to Kafka..."):
        send_data_to_kafka(header=header, data=[f"40.{i}42", f"-74.{i}037", f"B2000{i}"])
        sleep(time_step)


if __name__ == "__main__":
    # send_real_data_to_kafka()
    send_fake_data_to_kafka(70, 2)
