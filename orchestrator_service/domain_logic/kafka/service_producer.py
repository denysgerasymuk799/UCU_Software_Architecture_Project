import json
import uuid

from aiokafka import AIOKafkaProducer
from kafka.errors import KafkaTimeoutError

from domain_logic.__constants import *
from config import kafka_loop, logger


def success_callback(logger_name, topic):
    logger.info(f"{str(logger_name)}: Successfully sent message to Topic: [{topic}].")


def error_callback(logger_name, topic):
    logger.error(f"{str(logger_name)}: Failed to send message to Topic: [{topic}].")


class ServiceProducer:
    def __init__(self, logger_name):
        self.__logger = logger_name
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda data: json.dumps(data).encode("utf-8"),
            loop=kafka_loop
        )

    async def send(self, topic, partition_key, message):
        await self.__producer.start()
        try:
            partition_key = str.encode(partition_key) if partition_key else uuid.uuid1().bytes
            await self.__producer.send_and_wait(topic=topic, key=partition_key, value=message)
            success_callback(self.__logger, topic)

        # if unable to fetch topic metadata, or unable to obtain memory buffer.
        except KafkaTimeoutError:
            self.__logger.error(f"Unable to send a message to [{topic}] topic.")
            await self.__producer.stop()
