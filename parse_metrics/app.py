import os
import json
from kafka import KafkaConsumer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
METRIC_TOPIC = os.environ.get("METRIC_TOPIC")

process_time_sum = 0
records_processed = 0
errors = 0


def aggregate_stats():
    """
    Aggregates list of metrics into sums and averages
    to give overall performance of microservice.
    Returns dict of form:
    {
      "Records_Processed": int,
      "Avg_Records_Per_Second": float
    }

    :param agg_dict: aggregate dict of lists
    :return: dict of form above
    """
    # If data is empty, don't do anything:
    if records_processed == 0:
        return {}

    return {
        "Records_Processed": records_processed,
        "Avg_Records_Per_Second":
            records_processed / process_time_sum,
        "Errors": errors
    }


if __name__ == '__main__':
    consumer = KafkaConsumer(
        METRIC_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        value_deserializer=lambda value: json.loads(value),
        consumer_timeout_ms=15000
    )

    # Consumer metrics from kafka topic
    # and add to metric_agg dict of lists
    for message in consumer:
        process_time_sum += message.value["processed_per_second"]
        records_processed += message.value["records_processed"]
        errors += message.value["errors"]

    # When we're done, aggregate results
    # And print off metrics
    result = aggregate_stats()
    print("PARSE METRICS")
    for key, val in result.items():
        print(key, ":", val)
    print()
