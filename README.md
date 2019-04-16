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

## POC Execution
Because this is built in docker, execution is pretty darn simple so long as you have docker on your machine, basically:
1. Clone this repository to a directory of your choosing. 
2. In one terminal window, run 'docker-compose -f docker-compose.kafka.yml up' and it will download the confluence docker images and start things up. Lots of scrolling text and then it will stop and is ready to use
3. In another terminal window, run 'docker-compose up' (make sure you're in the root directory of this project). That will start the sample log ingestion and streamings apps that follow.
4. Kick back, wait a minute or two, and check out the results (go to System Testing to see what that looks like).

## POC Testing
Given the burst of energy one Sunday afternoon that this project was birthed from, it was an unfortunate code-now-test-later sort of development. But I'd be remised if I didn't have *some* unit testing and example case results to prove that I'm not crazy!

### Unit Testing
Unit testing happens in the 'test' folder, as one might assume, and is only done on the main streaming apps data transformations. Not nearly as much code coverage as I'd feel comfortable deploying to production but hey, it's a POC :poop:

### System Testing
So for starters, a sample log file from an apache web server is in '/apache_server_log_producer'. Its about a minute of logs, with ~160,000 unique HTTP requests. Before I dove into Kafka, I wanted to see which IP addresses belonged to the bad guys. With some simple data transformations in 'log_parser_playground.py' and my the plotly library, it becomes quickly apparent:

![alt text](https://raw.githubusercontent.com/schwertJake/Kafka_DDOS_Detection/master/images/Number%20of%20Users%20and%20their%20Frequency%20of%20HTTP%20request.png "")

So the answer we're looking for is 991 unique IP addresses. Executing the program results in the follow output:

![alt text](https://raw.githubusercontent.com/schwertJake/Kafka_DDOS_Detection/master/images/cli_output_metrics_2gbRam_2cpu.PNG "")

The blacklisted IP addresses will be written to a file called 'blacklist.txt' with the timestamp of when they were found. That file resides in the docker image, but I pulled it out as an example, find it [here](https://github.com/schwertJake/Kafka_DDOS_Detection/blob/master/sample_blacklist.txt)

__And indeed, we found all 991 malicious IPs and wrote them to logs.blacklist__

The metrics (processing roughly 1400 logs per second at each streaming app) are from a docker VM with 2GB Ram and 2 CPUs. Out of curiousity, I scaled it vertically to 4GB Ram, 4CPU and got the following result:

![alt text](https://raw.githubusercontent.com/schwertJake/Kafka_DDOS_Detection/master/images/cli_output_metrics_4gbRam_4cpu.PNG "")

Which garnered a nice 10% bump up to 1650 messages per second.

## Production Changes
So, the POC worked, how would I change this for production?

I'm glad you asked. Among other small tweaks, mostly I would add persistance via a documentDB as shown in the below architecture:

![alt text](https://raw.githubusercontent.com/schwertJake/Kafka_DDOS_Detection/master/images/production_architecture.png "")

If you hadn't guessed, the blue objects are for data persistance.
Essentially, I would keep the existing architecture but add MongoDB (or your documentDB of choice) into the mix to persist the following things:
* Metric / Metadata of streaming app performance
* Full log file JSON documents
* Blacklisted IPs (though because this data is so simple, a KV database would work fine too, if you feel like standing up a second database)

## Scaling
All of the tech is already built to be scalable, yay! No SQL servers to migrate or any craziness like that. Nevertheless, scaleing to hundreds of thousands of visitors on multiple nodes poses some interesting problems.

My ramblings about scaling the system, in no particular order and at a high level, are below:
* Horizontally scale (obviously) the database(s) and kafka. Python streaming apps / microservices can be duplicated per node or as needed. Some testing is definitely required to find performance bottlenecks.
*  Kafka needs to be parralellized. This can be done with partitions. An important restriction in doing this is that kafka assigns a single partition to one consumer thread (within a group), so those numbers must be balanced. An article I really enjoyed about parralellism in Kafka that talks more about the subject is [here](https://www.confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster)
* One potential concern of mine is that the sliding window which finds malicious IP resides completely in the python streaming app and thus in memory. So memory of a node may become a concern if a single node has hundreds of thousands of logs and a long time window. Fixes to this would be keep the time window short - 30s to a minute, or just scale across more nodes to use more memory.
* The data persistance side of things should scale fine horizontally - it's a write heavy system, so consistancy can take a back burner to volume of data. MongoDB can [shard](https://docs.mongodb.com/manual/sharding) - one of the important considerations in doing so is the sharding key. Given the uniqueness and diferences of IP address string, I'd be inclined to use them as the shard key (perhaps hash them as well).

## Lessons Learned / Questions Remaining / Stuff I didn't know
I love these sort of explorations because I always do lots of stuff wrong, and therefore learn a ton. Some of my lessons learned from building this system:
* Metric aggregation is important but tough to impliment correctly. I'm still not sure if making seperate microservice apps just to collect metrics (or persist them to a DB in production) is the best architecture. It felt life a lot of ctr+c, ctrl+v, but I'm not totally sure how I'd set it up differently. Perhaps inheritance?
* Speaking of metric aggregation; at first implimentation, I recorded the 'cycle' time to process a single message, and then appended that to a list to later average as a throughput/speed metric. In chasing performance (and memory utilization), I switched that to measuring how long it took to process X messages (1000, 10000, etc) and then diving that by the count of messages processed as a throughput metric. This sounded great at first, and works fine if the kafka pipeline is not empty (the streaming apps can't keep up), but if traffic slows down, this metric looses validity.
* There has got to be a better way to set these apps up for unit testing. Without a deep and frustrating dive into the world of mocking, it was difficult to test a lot of my code due to dependencies in the environment or code structure.
* Kafka is still a bit of a black box in practice. I academically understand it, but this project didn't really show the wizard behind the wall. I think this would come when scaling this out across many nodes.
* Docker compose rocks. Not really a lesson learned, but for developing test stuff like this, I was up and running in basically no time. That said, in a rapid-code-then-run-then-fix environment, it's important to tear down the images (`docker-compose down --rmi all`), then rebuild them. Not just stop them. Took me a long time to realize why my changes weren't taking effect.
 
