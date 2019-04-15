import os
import json
import time
from kafka import KafkaConsumer

KAFKA_BROKER_URL = os.environ.get('KAFKA_BROKER_URL')
FROM_TOPIC = os.environ.get('FROM_TOPIC')


if __name__ == '__main__':
    consumer = KafkaConsumer(
        FROM_TOPIC,
        bootstrap_servers=KAFKA_BROKER_URL,
        value_deserializer=lambda value: json.loads(value),
        consumer_timeout_ms=60000
    )

    # Consumer metrics from kafka topic
    with open('blacklist.txt', 'w') as f:
        f.write("BLACKLIST\n")
        for message in consumer:
            f.write(str(time.time())+" : "+message.value["IP"]+"/n")