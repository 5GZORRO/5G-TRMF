from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json


class Producer():


    admin_client = KafkaAdminClient(bootstrap_servers="172.28.3.196:9092",client_id='test')
    producer = KafkaProducer(bootstrap_servers='172.28.3.196:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def createTopic(self, topic_name):
        """ This function allows generating new kafka topics where the topic name is composed by trustor's DID +
        trustee's DID + offer's DID """

        global admin_client
        global producer

        #Check if topic exits
        if topic_name not in self.admin_client.list_topics():
            topic_list = []
            topic_list.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))
            self.admin_client.create_topics(new_topics=topic_list, validate_only=False)
            return 200

        return 400

    def sendMessage(self, topic_name, key, message):
        """ This method is responsible for recording a message in a Kafka topic """
        global admin_client
        global producer

        self.producer.send(topic_name, key=str.encode(key), value=message)
        self.producer.flush()

        return 1

"""producer = Producer()
message = {"trustorDID": "99lm6s88-jv84-ii57-qq53-6166qvw8l3zt", "trusteeDID": "90afc0f6-34fb-4c09-a3c0-f880078b6e76",
           "offerDID": "MzCciMdUNovcBSbUspeQHf", "interactionNumber": 1, "totalInteractionNumber": 2,
           "currentInteractionNumber": 3,}

creation = producer.createTopic("test1")


if creation == 200:
    print("Generation of a new Topic")
    producer.sendMessage("test1","did1234", message)
    print("Message sent")
else:
    producer.sendMessage("test1","did12345", message)
    print("Message sent after creation")"""
