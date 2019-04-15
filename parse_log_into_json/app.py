import os
import json
import time
from datetime import datetime
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
FROM_TOPIC = os.environ.get('FROM_TOPIC')
TO_TOPIC = os.environ.get("TO_TOPIC")
METRIC_TOPIC = os.environ.get("METRIC_TOPIC")
METRIC_CYCLE = int(os.environ.get("METRIC_CYCLE"))


def parse_apache_log_line(log_line: str) -> dict:
    """
    Parses a log line in apache log format to a
    usable dict of form
    {
        "IP": str,
        "Time": int,
        "Request_Method": str,
        "Request_Resource": str,
        "Request_Protocol": str,
        "Status_Code": int,
        "Payload_Size": int,
        "Referer": str,
        "User_Agent": str
    }

    :param log_line: str in apache log format
    :return: dict of form above
    """
    split_ws = log_line.split(" ")
    return {
        "IP": split_ws[0],
        "Time": get_time_epoch(split_ws[3][1:], split_ws[4][:-1]),
        "Request_Method": split_ws[5][1:],
        "Request_Resource": split_ws[6],
        "Request_Protocol": split_ws[7][:-1],
        "Status_Code": int(split_ws[8]),
        "Payload_Size": int(split_ws[9]),
        "Referer": split_ws[10].replace("\"", ""),
        "User_Agent": " ".join(split_ws[11:-1]).replace("\"", "")
    }


def get_time_epoch(time_stamp: str, time_zone: str) -> float:
    """
    Takes a time stamp and time zone from apache log format
    and converts it into epoch time, returning an int

    :param time_stamp: time stamp (str) in apache log format
    :param time_zone: time zone (str) in apache log format
    :return: time (epoch) as int
    """
    d = datetime.strptime(time_stamp+" "+time_zone, "%d/%b/%Y:%H:%M:%S %z")
    return int(d.timestamp())


if __name__ == '__main__':
    consumer = KafkaConsumer(
        FROM_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        value_deserializer=lambda value: json.loads(value),
        consumer_timeout_ms=5000
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode(),
    )

    count = 0
    start = time.time()

    for message in consumer:

        # Metric Increments
        count += 1

        # Transform and Publish Data
        transformed_data: dict = \
            parse_apache_log_line(message.value["line"])
        producer.send(TO_TOPIC, value=transformed_data)

        # Metric Aggregation
        if count >= METRIC_CYCLE:
            metrics = {
                "processed_per_second": count/(time.time() - start),
                "records_processed": count,
                "end_ts": time.time()
            }
            producer.send(METRIC_TOPIC, value=metrics)
            count = 0
            start = time.time()
