import json
# from kafka import KafkaProducer
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from kafka.errors import KafkaTimeoutError

from domain_logic.__constants import *
from config import loop2, logger


# def success_callback(logger, metadata):
#     logger.info(f"{str(logger)}: Successfully sent message to Topic: [{metadata.topic}].")
#
#
# def error_callback(logger, metadata):
#     logger.error(f"{str(logger)}: Failed to send message to Topic: [{metadata.topic}].")


def success_callback(logger_name, topic):
    logger.info(f"{str(logger_name)}: Successfully sent message to Topic: [{topic}].")


def error_callback(logger_name, topic):
    logger.error(f"{str(logger_name)}: Failed to send message to Topic: [{topic}].")


class ServiceProducer:
    def __init__(self, logger):
        self.__logger = logger
        self.__producer = AIOKafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda data: json.dumps(data).encode("utf-8"),
            loop=loop2
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
