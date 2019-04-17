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

    # Read through log file line by line,
    # Create JSON object of {"line": str}, and post
    # to Kafka topic logs.raw
    with open('apache-access-log.txt') as file:
        # Post to Kafka:
        for line in file:
            start = time.time()

            transaction: dict = {'line': line}
            producer.send(TRANSACTIONS_TOPIC, value=transaction)
            elapsed_t = time.time() - start

            # Metric Aggregation:
            metrics = {
                "process_time": elapsed_t,
                "records_processed": 1,
            }
            producer.send(METRIC_TOPIC, value=metrics)
