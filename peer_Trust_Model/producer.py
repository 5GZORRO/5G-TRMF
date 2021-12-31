from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json


class Producer():

    admin_client = KafkaAdminClient(bootstrap_servers="kafka:9093",client_id='test')
    producer = KafkaProducer(bootstrap_servers='kafka:9093', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    def createTopic(self, topic_name):
        """ This function allows generating new kafka topics where the topic name is composed by trustor's DID +
        trustee's DID + offer's DID """
        #Check if topic exits
        if topic_name not in self.admin_client.list_topics():
            topic_list = []
            topic_list.append(NewTopic(name=topic_name, num_partitions=1, replication_factor=1))
            self.admin_client.create_topics(new_topics=topic_list, validate_only=False)

        return 1

    def sendMessage(self, topic_name, key, message):
        """ This method is responsible for recording a message in a Kafka topic """
        self.producer.send(topic_name, key=str.encode(key), value=message)
        self.producer.flush()

        return 1
