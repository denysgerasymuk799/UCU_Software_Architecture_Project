import logging
import configparser

from json import dumps
from kafka import KafkaProducer

from src.custom_logger import MyHandler

logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(MyHandler())


def on_send_success(record_metadata):
    logging.info("Producer: Record metadata")
    logging.info(f"Topic: {record_metadata.topic}")
    logging.info(f"Partition: {record_metadata.partition}")
    logging.info(f"Offset: {record_metadata.offset}")
    logging.info(f"Timestamp: {record_metadata.timestamp}\n\n")


def on_send_error(excp):
    logging.error('Producer: Got errback', exc_info=excp)


class TransactionProducer:
    def __init__(self):
        # Reading Configs
        config = configparser.ConfigParser()
        config.read("config.ini")

        # Setting configuration values
        ip_address = config['Producer']['ip_address']
        self.__producer = KafkaProducer(bootstrap_servers=[ip_address],
                                        api_version=(2, 8, 0),
                                        acks='all',
                                        retries=5,
                                        max_in_flight_requests_per_connection=1,
                                        value_serializer=lambda x: dumps(x).encode('utf-8'))

    def send_messages(self, topic, messages):
        for message in messages:
            self.__producer.send(topic, value=message).add_callback(on_send_success) \
                .add_errback(on_send_error)

            self.__producer.flush()

        print("All messages are added. len(messages) -- ", len(messages))
