import os
import json
import time
from kafka import KafkaProducer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
TRANSACTIONS_TOPIC = os.environ.get('TRANSACTIONS_TOPIC')
METRIC_TOPIC = os.environ.get("METRIC_TOPIC")
METRIC_CYCLE = int(os.environ.get("METRIC_CYCLE"))

if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER_URL,
        value_serializer=lambda value: json.dumps(value).encode(),
    )

    # Initialize Starting Metrics
    count = 0
    start = time.time()

    # Read through log file line by line,
    # Create JSON object of {"line": str}, and post
    # to Kafka topic logs.raw
    with open('apache-access-log.txt') as file:

        # Post to Kafka:
        for line in file:
            count += 1
            transaction: dict = {'line': line}
            producer.send(TRANSACTIONS_TOPIC, value=transaction)

        # Metric Aggregation:
        if count >= METRIC_CYCLE:
            metrics = {
                "processed_per_second": count / (time.time() - start),
                "records_processed": count,
                "end_ts": time.time()
            }
            producer.send(METRIC_TOPIC, value=metrics)
            count = 0
            start = time.time()

    # Final Metric Aggregation:
    metrics = {
        "processed_per_second": count / (time.time() - start),
        "records_processed": count,
        "end_ts": time.time()
    }
    producer.send(METRIC_TOPIC, value=metrics)
