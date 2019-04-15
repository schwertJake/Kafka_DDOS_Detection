import os
import json
import time
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
FROM_TOPIC = os.environ.get('FROM_TOPIC')
TO_TOPIC = os.environ.get("TO_TOPIC")
METRIC_TOPIC = os.environ.get("METRIC_TOPIC")
METRIC_CYCLE = int(os.environ.get("METRIC_CYCLE"))


def trim_to_ip_ts(parsed_data: dict) -> dict:
    """
    Pairs down full data set from apache log file
    to just the IP address and timestamp, to be
    counted in sliding window lated

    :param parsed_data: full dict of log line data
    :return: dict of form {"IP": str, "TS": ts}
    """
    return {
        "IP": parsed_data['IP'],
        "TS": parsed_data['Time']
    }


if __name__ == '__main__':
    consumer = KafkaConsumer(
        FROM_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        value_deserializer=lambda value: json.loads(value),
    )
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode(),
    )

    # Metric initialization
    count = 0
    start = time.time()

    for message in consumer:

        # Metric Increments
        count += 1

        # Transform and Publish Data
        transformed_data: dict = trim_to_ip_ts(message.value)
        producer.send(TO_TOPIC, value=transformed_data)

        # Metric Aggregation
        if count >= 1000:
            metrics = {
                "processed_per_second": count / (time.time() - start),
                "records_processed": count,
                "end_ts": time.time()
            }
            producer.send(METRIC_TOPIC, value=metrics)
            count = 0
            start = time.time()
