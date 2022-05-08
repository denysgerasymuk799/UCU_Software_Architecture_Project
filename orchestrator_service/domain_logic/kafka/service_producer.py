import json
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

    async def send(self, topic, message):
        await self.__producer.start()
        try:
            await self.__producer.send_and_wait(topic=topic, value=message)
            success_callback(self.__logger, topic)
            # \
            # .add_callback(success_callback, self.__logger) \
            #     .add_errback(error_callback, self.__logger)
            # self.__producer.flush()

        # if unable to fetch topic metadata, or unable to obtain memory buffer.
        except KafkaTimeoutError:
            self.__logger.error(f"Unable to send a message to [{topic}] topic.")
            await self.__producer.stop()
