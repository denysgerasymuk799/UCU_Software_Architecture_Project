from domain_logic.__constants import *
from kafka import KafkaProducer
from kafka.errors import KafkaTimeoutError
import json
import time


def success_callback(logger, metadata):
    logger.info(f"{str(logger)}: Successfully sent message to Topic: [{metadata.topic}].")


def error_callback(logger, metadata):
    logger.error(f"{str(logger)}: Failed to send message to Topic: [{metadata.topic}].")


class ServiceProducer:
    def __init__(self, logger):
        self.__logger = logger
        self.__producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda data: json.dumps(data).encode("utf-8")
        )

    def send(self, topic, message):
        try:
            self.__producer.send(topic=topic, value=message) \
                .add_callback(success_callback, self.__logger) \
                .add_errback(error_callback, self.__logger)
            self.__producer.flush()
        # if unable to fetch topic metadata, or unable to obtain memory buffer.
        except KafkaTimeoutError:
            self.__logger.error(f"Unable to send a message to [{topic}] topic.")


if __name__ == '__main__':
    producer = ServiceProducer("ServiceProducer")
    message_ = {
        "eventName": Events.TRANSACTION_REQUEST.value,
        "messageType": MESSAGE_TYPE_REQUEST,
        "responseType": RESPONSE_SUCCESS,
        "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
        "message": "",
        "data": {
            "cardholder_id": "624f270467c299bf18be0d53",
            "receiver_id": "624f270467c299bf18be0d55",
            "amount": 867,
        }
    }
    producer.send("TransactionService", message_)
    time.sleep(1)
    # 3655
    message_ = {
        "eventName": Events.TRANSACTION_REQUEST.value,
        "messageType": MESSAGE_TYPE_REQUEST,
        "responseType": RESPONSE_SUCCESS,
        "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
        "message": "",
        "data": {
            "cardholder_id": "624f270467c299bf18be0d53",
            "receiver_id": "624f270467c299bf18be0d56",
            "amount": 127,
        }
    }
    producer.send("TransactionService", message_)
