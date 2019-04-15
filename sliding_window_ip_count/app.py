import os
import json
import time
from kafka import KafkaConsumer, KafkaProducer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
FROM_TOPIC = os.environ.get('FROM_TOPIC')
TO_TOPIC = os.environ.get("TO_TOPIC")
WINDOW_SIZE = int(os.environ.get("WINDOW_SIZE"))*60
THROTTLE_LIMIT = int(os.environ.get("THROTTLE_LIMIT_PER_MIN"))
METRIC_TOPIC = os.environ.get("METRIC_TOPIC")
METRIC_CYCLE = int(os.environ.get("METRIC_CYCLE"))

sliding_window = {}
blacklist = []


def put_sliding_window(ip_ts: dict):
    """
    Takes a dict of form {"IP": str, "TS": int}
    Puts into a sliding window dict of lists that counts
    the number of timestamps in a certain period. If that
    count exceeds the threshold, the IP address is "blacklisted"
    and added to the blacklist list and the IP is posted to a
    kafka topic called logs.blacklist

    :param ip_ts: dict of form {"IP": str, "TS": ts}
    :return: None if not new blacklisted IP or dict of form
        {
            "IP": str,
            "Req_Per_Min_Exceeded": int
        }
        if the IP address is newly blacklisted
    """
    ip = ip_ts["IP"]
    ts = ip_ts["TS"]

    # If IP is already blacklisted, ignore it
    if ip in blacklist:
        return None

    # IF IP is new, add it to sliding window keys
    if ip not in sliding_window.keys():
        sliding_window[ip] = {'ts': [ts],
                              'count': 1}

    # Otherwise, add timestamp to sliding window
    # And slide the window as necessary, keeping
    # track of count
    else:
        while sliding_window[ip]['ts'] != [] \
                and ts - WINDOW_SIZE > sliding_window[ip]['ts'][0]:
            del sliding_window[ip]['ts'][0]
            sliding_window[ip]['count'] -= 1
        sliding_window[ip]['ts'].append(ts)
        sliding_window[ip]['count'] += 1

        # If the count exceeds the THROTTLE_LIMIT,
        # return the IP address to be sent to logs.blacklist
        if sliding_window[ip]['count'] \
                >= THROTTLE_LIMIT * (WINDOW_SIZE / 60):
            blacklist.append(ip)
            return {
                "IP": ip,
                "Req_Per_Min_Exceeded": THROTTLE_LIMIT
            }

    return None


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
    blacklisted = 0
    start = time.time()

    for message in consumer:

        # Metric Increments
        count += 1

        # Transform and Publish Data
        transaction: dict = put_sliding_window(message.value)
        if transaction:
            blacklisted += 1
            producer.send(TO_TOPIC, value=transaction)

        # Metric Aggregation
        if count >= 1000:
            metrics = {
                "processed_per_second": count /(time.time() - start),
                "records_processed": count,
                "blacklisted_ips": blacklisted,
                "end_ts": time.time()
            }
            producer.send(METRIC_TOPIC, value=metrics)
            count = 0
            blacklisted = 0
            start = time.time()
