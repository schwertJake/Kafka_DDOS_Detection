import os
import json
from kafka import KafkaConsumer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
METRIC_TOPIC = os.environ.get("METRIC_TOPIC")

ingest_metric_agg = {
    "processed_per_second": [],
    "records_processed": [],
    "errors": [],
    "end_ts": []
}


def aggregate_stats(agg_dict: dict):
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
    if agg_dict["processed_per_second"] == []:
        return {}

    return {
        "Records_Processed": sum(agg_dict["records_processed"]),
        "Avg_Records_Per_Second":
            sum(agg_dict["processed_per_second"]) /
            len(agg_dict["processed_per_second"]),
        "Errors": sum(agg_dict["errors"])
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
        for key, val in message.value.items():
            ingest_metric_agg[key].append(val)

    # When we're done, aggregate results
    # And print off metrics
    result = aggregate_stats(ingest_metric_agg)
    print("TRIM METRICS")
    for key, val in result.items():
        print(key, ":", val)
    print()
