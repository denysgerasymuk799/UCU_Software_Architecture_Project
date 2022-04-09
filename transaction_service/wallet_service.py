from src.__constants import *
from src.__utils import get_logger
from src.__db import WalletServiceDatabase, db, ReservedTransaction
from producer import ServiceProducer
from kafka import KafkaConsumer
import datetime
import asyncio
import json
import time


class WalletServiceConsumer:
    def __init__(self, topics=WALLET_TOPIC):
        self.__logger = get_logger(name="WalletService")
        # Setup the consumer.
        self.__consumer = KafkaConsumer(
            topics,
            bootstrap_servers=[KAFKA_BROKER],
            value_deserializer=lambda data: json.loads(data.decode("utf-8")),
            group_id=CONSUMER_GROUP
        )
        self.__consumer.subscribe([topics])
        # Create a unique producer for the service.
        self.__producer = ServiceProducer(self.__logger)
        # Connect to WalletServiceDB.
        self.__db = WalletServiceDatabase(db)

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
                if event == Events.TRANSACTION_CREATED.value:
                    event_loop.run_until_complete(self.__reserve_balance(data))
                elif event == Events.TRANSACTION_PENDING.value:
                    event_loop.run_until_complete(self.__process_payment(data))
                elif event == Events.RESERVATION_CANCELL.value:
                    event_loop.run_until_complete(self.__cancell_reservation(data))

                self.__consumer.commit()
                time.sleep(1)

    async def __reserve_balance(self, data):
        # Create a transaction instance.
        transaction = ReservedTransaction(
            wallet_id=data["cardholder_id"],
            amount=data["amount"],
            timestamp=datetime.datetime.utcnow()
        )

        # Try reserve money.
        transaction_id = await self.__db.reserve_transaction_amount(data["transaction_id"], transaction)

        # Mark operation event as successful if reserved.
        if transaction_id:
            event_name = Events.RESERVATION_SUCCESS.value
            message = "Operation success."
        else:
            event_name = Events.RESERVATION_FAILURE.value
            message = "WalletServiceError: Unable to execute current operation. Not enough balance."

        # Send a response to a TransactionService.
        message = {
            "eventName":    event_name,
            "messageType":  MESSAGE_TYPE_RESPONSE,
            "responseType": RESPONSE_SUCCESS,
            "producer":     WALLET_SERVICE_PRODUCER_NAME,
            "message":      message,
            "data":         {
                "transaction_id": data["transaction_id"]
            }
        }
        self.__producer.send(TRANSACTIONS_TOPIC, message)
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: RESERVED.")

    async def __process_payment(self, data):
        # Try execute transaction.
        response = await self.__db.execute_transaction(data["transaction_id"])
        if response:
            event_name = Events.TRANSACTION_SUCCESS.value
            message = "Operation success."
        else:
            event_name = Events.TRANSACTION_FAILURE.value
            message = "WalletServiceError: Failed to execute transaction."

        # Send a response to a TransactionService.
        message = {
            "eventName": event_name,
            "messageType": MESSAGE_TYPE_RESPONSE,
            "responseType": RESPONSE_SUCCESS,
            "producer": WALLET_SERVICE_PRODUCER_NAME,
            "message": message,
            "data": {
                "transaction_id": data["transaction_id"]
            }
        }
        self.__producer.send(TRANSACTIONS_TOPIC, message)
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: COMPLETE.")

    async def __cancell_reservation(self, data):
        response = self.__db.calcel_reservation(data["transaction_id"])
        if response:
            event_name = Events.TRANSACTION_CANCELLED.value
            message = "Operation success."
        else:
            event_name = Events.TRANSACTION_FAILURE.value
            message = "WalletServiceError: Failed to calcel transaction."

        # Send a response to a TransactionService.
        message = {
            "eventName": event_name,
            "messageType": MESSAGE_TYPE_RESPONSE,
            "responseType": RESPONSE_SUCCESS,
            "producer": WALLET_SERVICE_PRODUCER_NAME,
            "message": message,
            "data": {
                "transaction_id": data["transaction_id"]
            }
        }
        self.__producer.send(TRANSACTIONS_TOPIC, message)
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: CANCELLED.")


if __name__ == '__main__':
    consumer = WalletServiceConsumer()
    consumer.receive()
