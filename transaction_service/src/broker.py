from kafka.admin import KafkaAdminClient, NewTopic
from __constants import *


class KafkaBroker:
    def __init__(self):
        self.__broker = KafkaAdminClient(bootstrap_servers=[KAFKA_BROKER], client_id='test')

    def add_topic(self, topic_name):
        topic_list = [NewTopic(name=topic_name, num_partitions=1, replication_factor=1)]
        self.__broker.create_topics(new_topics=topic_list, validate_only=False)

    def remove_topic(self, topic_name):
        topic_list = [topic_name]
        self.__broker.delete_topics(topics=topic_list)


if __name__ == '__main__':
    broker = KafkaBroker()
    broker.add_topic("TransactionService")
    broker.add_topic("WalletService")
