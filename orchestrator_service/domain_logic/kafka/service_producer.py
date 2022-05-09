import uuid
import json
from aiokafka import AIOKafkaProducer
from confluent_kafka import Producer, KafkaError
from kafka.errors import KafkaTimeoutError

import domain_logic.kafka.ccloud_lib as ccloud_lib
from domain_logic.__constants import *
from config import kafka_loop, logger


def success_callback(logger_name, topic):
    logger.info(f"{str(logger_name)}: Successfully sent message to Topic: [{topic}].")


def error_callback(logger_name, topic):
    logger.error(f"{str(logger_name)}: Failed to send message to Topic: [{topic}].")


class ServiceProducer:
    def __init__(self, logger_name):
        self.__logger = logger_name
        # self.__producer = AIOKafkaProducer(
        #     bootstrap_servers=[KAFKA_BROKER],
        #     value_serializer=lambda data: json.dumps(data).encode("utf-8"),
        #     loop=kafka_loop
        # )
        conf = ccloud_lib.read_ccloud_config(KAFKA_CONFIG_FILE)

        # Create Producer instance
        producer_conf = ccloud_lib.pop_schema_registry_params_from_config(conf)
        self.__producer = Producer(producer_conf)

    def send(self, topic, message):
        delivered_records = 0

        # Optional per-message on_delivery handler (triggered by poll() or flush())
        # when a message has been successfully delivered or
        # permanently failed delivery (after retries).
        def acked(err, msg, delivered_records=delivered_records):
            """Delivery report handler called on
            successful or failed delivery of message
            """
            if err is not None:
                print("Failed to deliver message: {}".format(err))
            else:
                delivered_records += 1
                print("Produced record to topic {} partition [{}] @ offset {}"
                      .format(msg.topic(), msg.partition(), msg.offset()))

        # await self.__producer.start()
        try:
            self.__producer.produce(topic=topic, key=uuid.uuid1().bytes,
                                    value=json.dumps(message).encode(), on_delivery=acked)
            # success_callback(self.__logger, topic)
            self.__producer.flush()

        # if unable to fetch topic metadata, or unable to obtain memory buffer.
        except KafkaTimeoutError:
            self.__logger.error(f"Unable to send a message to [{topic}] topic.")
            # await self.__producer.stop()
