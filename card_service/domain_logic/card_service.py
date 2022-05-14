from database.__db import CardServiceOperator, ReservedTransaction
from database.__cassandra_client import CassandraClient
from domain_logic.__utils import get_logger
from domain_logic.__constants import *

import json
import uuid


client = CassandraClient(
    host=CASSANDRA_HOST,
    port=CASSANDRA_PORT,
    keyspace=CASSANDRA_KEYSPACE,
    username=AMAZOM_KEYSPACES_USERNAME,
    password=AMAZOM_KEYSPACES_PASSWORD
)
client.connect()


class CardService:
    """
    Service for card balance reservation and transaction execution.
    """
    def __init__(self):
        self.__logger = get_logger(name=CARD_TOPIC)
        self.__db = CardServiceOperator(client)

    async def topup_balance(self, data: dict, transaction_service_topic):
        """
        Top up card balance for specified cardId.

        :param data: (dict) - transaction parameters.
        :param transaction_service_topic: (faust.topic) - topic to respond to after operation completion.
        """
        # Top up the balance from the db side.
        response = self.__db.topup_balance(data["card_id"], data["amount"])

        # Check if balance was updated.
        if not response:
            event_name = Events.TRANSACTION_FAILURE.value
            message = "Couldn't top up card balance."
        else:
            event_name = Events.TRANSACTION_SUCCESS.value
            message = "Card balance updated."

        # Send a response to a TransactionService.
        message = {
            "eventName":    event_name,
            "messageType":  MESSAGE_TYPE_RESPONSE,
            "responseType": RESPONSE_SUCCESS,
            "producer":     CARD_SERVICE_PRODUCER_NAME,
            "message":      message,
            "data": {
                "transaction_id": data["transaction_id"],
                "card_id": data["card_id"]
            }
        }
        await transaction_service_topic.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: COMPLETE.")

    async def reserve_balance(self, data: dict, transaction_service_topic):
        """
        Reserve card balance for the newly created transaction.

        :param data: (dict) - transaction parameters.
        :param transaction_service_topic: (faust.topic) - topic to respond to after operation completion.
        """
        # Create a transaction instance.
        transaction = ReservedTransaction(
            transaction_id=data["transaction_id"],
            card_id=data["card_id"],
            receiver_card_id=data["receiver_card_id"],
            amount=data["amount"],
            date=data["date"]
        )

        # Try reserve money.
        transaction_id = self.__db.reserve_transaction_amount(transaction)

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
            "producer":     CARD_SERVICE_PRODUCER_NAME,
            "message":      message,
            "data":         {
                "transaction_id": transaction.transaction_id,
                "card_id": transaction.card_id
            }
        }
        await transaction_service_topic.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{transaction.transaction_id}]. Status: RESERVED.")

    async def process_payment(self, data: dict, transaction_service_topic):
        """
        Execute transaction.

        :param data: (dict) - transaction parameters.
        :param transaction_service_topic: (faust.topic) - topic to respond to after operation completion.
        """
        # Try execute transaction.
        response = self.__db.execute_transaction(data["card_id"], data["transaction_id"])
        if response:
            event_name = Events.TRANSACTION_SUCCESS.value
            message = "Operation success."
        else:
            event_name = Events.TRANSACTION_FAILURE.value
            message = "WalletServiceError: Failed to execute transaction."

        # Send a response to a TransactionService.
        message = {
            "eventName":    event_name,
            "messageType":  MESSAGE_TYPE_RESPONSE,
            "responseType": RESPONSE_SUCCESS,
            "producer":     CARD_SERVICE_PRODUCER_NAME,
            "message":      message,
            "data": {
                "transaction_id": data["transaction_id"],
                "card_id": data["card_id"]
            }
        }
        await transaction_service_topic.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: COMPLETE.")

    async def cancel_reservation(self, data: dict, transaction_service_topic):
        """
        Cancel transaction reservation by specified cardId and transactionId.

        :param data: (dict) - cancelation parameters.
        :param transaction_service_topic: (faust.topic)
        """
        self.__db.cancel_reservation(data["card_id"], data["transaction_id"])

        # Send a response to a TransactionService.
        message = {
            "eventName":    Events.TRANSACTION_CANCELLED.value,
            "messageType":  MESSAGE_TYPE_RESPONSE,
            "responseType": RESPONSE_SUCCESS,
            "producer":     CARD_SERVICE_PRODUCER_NAME,
            "message":      "",
            "data": {
                "transaction_id": data["transaction_id"],
                "card_id": data["card_id"]
            }
        }
        await transaction_service_topic.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: CANCELLED.")
