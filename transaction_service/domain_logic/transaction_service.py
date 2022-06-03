from database.__db import TransactionServiceOperator, Transaction
from database.__cassandra_client import CassandraClient
from domain_logic.__constants import *
from domain_logic.__utils import get_logger
from datetime import datetime

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


class TransactionService:
    """
    Service for transaction processing.
    Delegates balance reservation and transaction execution to CardService.
    """
    def __init__(self):
        self.__logger = get_logger(name=TRANSACTIONS_TOPIC)
        self.__db = TransactionServiceOperator(client)

    async def create_topup_transaction(self, data: dict, card_service_topic):
        """
        Create balance top up transaction record in the database.
        Notify card service to top up balance for the current transaction.

        :param data: (dict) - transaction parameters.
        :param card_service_topic: (faust.topic)
        """
        record = Transaction(
            transaction_id=data["transaction_id"],
            card_id=data["card_id"],
            receiver_card_id=TOP_UP_ACTIVITY,
            amount=data["amount"],
            status=TRANSACTION_NEW_STATUS,
            date=datetime.utcnow().strftime("%Y-%m-%d")
        )
        # Create an entry in the Transaction table with NEW status.
        self.__db.create_transaction_record(record)

        message = {
            "eventName": Events.TRANSACTION_TOPUP.value,
            "messageType": MESSAGE_TYPE_REQUEST,
            "responseType": RESPONSE_SUCCESS,
            "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
            "message": "",
            "data": {
                "transaction_id": record.transaction_id,
                "card_id": record.card_id,
                "receiver_card_id": record.receiver_card_id,
                "amount": record.amount,
                "status": record.status,
                "date": record.date
            }
        }
        partition_key = str.encode(record.card_id) if record.card_id else uuid.uuid1().bytes
        await card_service_topic.send(key=partition_key, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{record.transaction_id}]. Status: {TRANSACTION_NEW_STATUS}.")

    async def create_transaction(self, data: dict, card_service_topic):
        """
        Create transaction record in the database.
        Notify card service to reserve balance for the current transaction.

        :param data: (dict) - transaction parameters.
        :param card_service_topic: (faust.topic)
        """
        record = Transaction(
            transaction_id=data["transaction_id"],
            card_id=data["card_id"],
            receiver_card_id=data["receiver_card_id"],
            amount=data["amount"],
            status=TRANSACTION_NEW_STATUS,
            date=datetime.utcnow().strftime("%Y-%m-%d")
        )
        # Create an entry in the Transaction table with NEW status.
        self.__db.create_transaction_record(record)

        message = {
            "eventName":    Events.TRANSACTION_CREATED.value,
            "messageType":  MESSAGE_TYPE_REQUEST,
            "responseType": RESPONSE_SUCCESS,
            "producer":     TRANSACTION_SERVICE_PRODUCER_NAME,
            "message":      "",
            "data": {
                "transaction_id": record.transaction_id,
                "card_id": record.card_id,
                "receiver_card_id": record.receiver_card_id,
                "amount": record.amount,
                "status": record.status,
                "date": record.date
            }
        }
        partition_key = str.encode(record.receiver_card_id) if record.receiver_card_id else uuid.uuid1().bytes
        await card_service_topic.send(key=partition_key, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{record.transaction_id}]. Status: {TRANSACTION_NEW_STATUS}.")

    async def execute_transaction(self, data, card_service_topic):
        """
        Send a message to execute transaction to CardService.

        :param data: (dict) - transaction parameters.
        :param card_service_topic: (faust.topic)
        """
        # Get a transaction record.
        record = self.__db.get_transaction_record(data["transaction_id"])
        transaction_id, card_id, receiver_card_id, amount, status, date = record
        # Mark a transaction as such that is waiting to be executed.
        self.__db.update_transaction_status(transaction_id, TRANSACTION_PENDING_STATUS)

        # Utilize data somehow.
        message = {
            "eventName":    Events.TRANSACTION_PENDING.value,
            "messageType":  MESSAGE_TYPE_REQUEST,
            "responseType": RESPONSE_SUCCESS,
            "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
            "message":      "",
            "amount": amount,
            "date": date,
            "data": {
                "transaction_id": transaction_id,
                "card_id": card_id
            }
        }
        partition_key = str.encode(card_id) if card_id else uuid.uuid1().bytes
        await card_service_topic.send(key=partition_key, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: {TRANSACTION_PENDING_STATUS}.")

    async def send_transaction_result(self, transaction_id: str, results_topic):
        """
        Send transaction execution status to the Results topic.

        :param transaction_id: (str) - unique id of transaction.
        :param results_topic: (faust.topic)
        """
        # Get transaction record.
        record = self.__db.get_transaction_record(transaction_id)
        transaction_id, card_id, receiver_card_id, amount, status, date = record

        message = {
            "transaction_id": transaction_id,
            "card_id": card_id,
            "receiver_card_id": TOP_UP_ACTIVITY if card_id == receiver_card_id else receiver_card_id,
            "amount": amount,
            "date": date,
            "status": "COMPLETED" if status == TRANSACTION_COMPLETED_STATUS else "FAILED"
        }
        # Send response to orchestrator.
        partition_key = str.encode(message["receiver_card_id"]) if message["receiver_card_id"] and message["receiver_card_id"] != TOP_UP_ACTIVITY\
            else uuid.uuid1().bytes
        await results_topic.send(key=partition_key, value=json.dumps(message).encode())

    async def set_transaction_completion_status(self, data: dict, status: str, results_topic):
        """
        Implicitly set the transaction status and send the results to the Results topic.

        :param data: (dict) - transaction parameters.
        :param status: (str) - transaction current status.
        :param results_topic: (faust.topic)
        """
        # Get a transaction record.
        self.__db.update_transaction_status(data["transaction_id"], status)

        await self.send_transaction_result(data["transaction_id"], results_topic)
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: {status}.")
