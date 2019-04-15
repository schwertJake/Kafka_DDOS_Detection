import os
import json
import time
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
FROM_TOPIC = os.environ.get('FROM_TOPIC')
TO_TOPIC = os.environ.get("TO_TOPIC")
METRIC_TOPIC = os.environ.get("METRIC_TOPIC")
METRIC_CYCLE = os.environ.get("METRIC_CYCLE")


def trim_to_ip_ts(parsed_data: dict) -> dict:
    """
    Pairs down full data set from apache log file
    to just the IP address and timestamp, to be
    counted in sliding window lated

    :param parsed_data: full dict of log line data
    :return: dict of form {"IP": str, "TS": ts}
    """
    try:
        trimmed_dict = {
            "IP": parsed_data['IP'],
            "TS": parsed_data['Time']
        }
        return trimmed_dict
    except KeyError:
        return {}


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

    # Metric initialization
    count = 0
    errors = 0
    start = time.time()

    for message in consumer:

        # Metric Increments
        count += 1

        # Transform and Publish Data
        transformed_data: dict = trim_to_ip_ts(message.value)
        if transformed_data != {}:
            producer.send(TO_TOPIC, value=transformed_data)
        else:
            errors += 1

        # Metric Aggregation
        if count >= int(METRIC_CYCLE):
            metrics = {
                "processed_per_second": count / (time.time() - start),
                "records_processed": count,
                "errors": errors,
                "end_ts": time.time()
            }
            producer.send(METRIC_TOPIC, value=metrics)
            count = 0
            start = time.time()
