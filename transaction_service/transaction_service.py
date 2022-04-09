from src.__constants import *
from src.__utils import get_logger
from src.__db import db, TransactionServiceDatabase, Transaction
from producer import ServiceProducer
from kafka import KafkaConsumer
import asyncio
import json
import time


class TransactionService:
    def __init__(self, topics=TRANSACTIONS_TOPIC):
        self.__logger = get_logger(name="TransactionService")
        self.__consumer = KafkaConsumer(
            topics,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda data: json.loads(data.decode("utf-8")),
            group_id=CONSUMER_GROUP
        )
        self.__consumer.subscribe([topics])
        self.__producer = ServiceProducer(self.__logger)
        self.__db = TransactionServiceDatabase(db)

    def receive(self):
        # Get event loop for the async operations execution.
        event_loop = asyncio.get_event_loop()

        while True:
            records_dict = self.__consumer.poll(max_records=100)
            for record in records_dict.values():
                # Get message details.
                message = record[0].value
                event, source, data = message['eventName'], message['producer'], message['data']
                # Log received message.
                self.__logger.info(f"Message received. Event: [{event}]. Source: [{source}].")

                # Do the required stuff.
                if event == Events.TRANSACTION_REQUEST.value:
                    event_loop.run_until_complete(self.__create_transaction(data))
                elif event == Events.RESERVATION_SUCCESS.value:
                    event_loop.run_until_complete(self.__execute_transaction(data))
                elif event == Events.TRANSACTION_SUCCESS.value:
                    event_loop.run_until_complete(self.__mark_transaction_complete(data))
                else:
                    self.__logger.info(f"Transaction: [{data['transaction_id']}]. Event: [{event}]")

                self.__consumer.commit()
                time.sleep(1)

    async def __create_transaction(self, data):
        # Create an entry in the Transaction table with NEW status.
        record = Transaction(
            cardholder_id=data["cardholder_id"],
            receiver_id=data["receiver_id"],
            amount=data["amount"],
            status="NEW"
        )
        transaction_id = await self.__db.create_transaction_record(record)

        message = {
            "eventName": Events.TRANSACTION_CREATED.value,
            "messageType": MESSAGE_TYPE_REQUEST,
            "responseType": RESPONSE_SUCCESS,
            "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
            "message": "",
            "data": {
                "transaction_id": str(transaction_id),
                "cardholder_id": record.cardholder_id,
                "receiver_id": record.receiver_id,
                "amount": record.amount,
                "status": record.status
            }
        }
        self.__producer.send(WALLET_TOPIC, message)
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: NEW.")

    async def __execute_transaction(self, data):
        # Get a transaction record.
        record = await self.__db.get_transaction_record(data["transaction_id"])
        # Mark a transaction as such that is waiting to be executed.
        transaction_id = await self.__db.update_transaction_record(data["transaction_id"], {"status": "PENDING"})

        # Utilize data somehow.
        message = {
            "eventName": Events.TRANSACTION_PENDING.value,
            "messageType": MESSAGE_TYPE_REQUEST,
            "responseType": RESPONSE_SUCCESS,
            "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
            "message": "",
            "data": {
                "transaction_id": transaction_id,
                "cardholder_id": record["cardholder_id"],
                "receiver_id": record["receiver_id"],
                "amount": record["amount"],
                "status": record["status"]
            }
        }
        self.__producer.send(WALLET_TOPIC, message)
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: PENDING.")

    async def __mark_transaction_complete(self, data):
        # Get a transaction record.
        transaction_id = await self.__db.update_transaction_record(data["transaction_id"], {"status": "COMPLETE"})
        # TODO: Send response to SAGA.
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: COMPLETE.")


if __name__ == '__main__':
    consumer = TransactionService()
    consumer.receive()
