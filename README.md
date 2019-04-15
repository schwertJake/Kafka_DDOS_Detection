# Kafka DDOS Detection
## Overview
This is a Proof of Concept software for detecting DDOS attacks on an apache web server via real time log analysis. Using Kafka as a messaging platform and python microservices as streaming applications, this system is able to effectively find malicious IP address in realtime.

## POC Architecture
Because this was coded up in very short time, the POC architectuere is stripped back version of what I would suggest for a production system (more on that later). The data pipeline is diagrammed below:

![alt text](https://raw.githubusercontent.com/schwertJake/Kafka_DDOS_Detection/master/images/poc_architecture.png "")

To better explain that messy diagram, objects are color coded as follows

![alt text](https://placehold.it/15/c3e2b6/000000?text=+) Core log data transformation pipeline

![alt text](https://placehold.it/15/bcafe5/000000?text=+) Metrics and metadata pipeline

![alt text](https://placehold.it/15/f4c79a/000000?text=+) DDOS detection pipeline

So at a top level, the following happens:

1. Raw log line from apache web server (or example document in this case) enters kafka at the logs.raw topic
2. That raw log (one long string) is parsed into a useful JSON object containing the IP, Timestamp, Resource Requested, and lots of other interesting information, and is publised to the logs.parse kafka topic
3. The parsed logs now enter the DDOS detection specific stream applications. The first one trim's down that JSON document to just the IP address and the timestamp, then publishes it to the logs.trim kafka topic.
4. These messages containing just the IP address and timestamp are entered into a sliding window where only timestamps in the last <user defined time> exist. If the count of timestamps within the window are greater than <user defined threshold>, the IP is considered overactive and malicious, and is published to a logs.blacklist topic for further use

## POC Deployment
My growing favorite way to develop projects like this is with docker. Running in a controlled environment on my local machine is simple, and I could deploy it to the cloud with minimum headache (famous last words, right?) if I needed to. So, of course, that is what I used.

Now, when researching on how to accomplish kafka+python in docker, I stumbled upon [this very helpful article from CodeSail](https://blog.florimondmanca.com/building-a-streaming-fraud-detection-system-with-kafka-and-python) and liked the idea of deploying kafka as a seperate service from the streaming apps. Therefore, Kafka (and Zookeeper) are assembled in 'docker-compose.kafka.yaml', and must be run seperately and in advance of the python streaming apps, which reside in 'docker-compose.yaml'. This makes for a really nice decoupling of the messaging engine from the streaming apps. The docker architecture is simply illustrated below:

![alt text](https://raw.githubusercontent.com/schwertJake/Kafka_DDOS_Detection/master/images/poc_docker.png "")

## POC Testing
Given the burst of energy one Sunday afternoon that this project was birthed from, it was an unfortunate code-now-test-later sort of development. But I'd be remised if I didn't have *some* unit testing and example case results to prove that I'm not crazy!

### Unit Testing
Unit testing happens in the 'test' folder, as one might assume, and is only done on the main streaming apps data transformations. Not nearly as much code coverage as I'd feel comfortable deploying to production but, hey, it's a POC :poop:

### System Testing


