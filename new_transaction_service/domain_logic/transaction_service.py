import json
import uuid

from domain_logic.__constants import *
from domain_logic.utils.__utils import get_logger
from database.__db import db, TransactionServiceDatabase, Transaction


class TransactionService:
    def __init__(self):
        self.__logger = get_logger(name=TRANSACTIONS_TOPIC)
        self.__db = TransactionServiceDatabase(db)

    async def create_transaction(self, data, wallet_topic_obj):
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
        await wallet_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: NEW.")

    async def execute_transaction(self, data, wallet_topic_obj):
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
        await wallet_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: PENDING.")

    async def mark_transaction_complete(self, data):
        # Get a transaction record.
        transaction_id = await self.__db.update_transaction_record(data["transaction_id"], {"status": "COMPLETE"})
        # TODO: Send response to SAGA.
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: COMPLETE.")
