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
        record = Transaction(
            user_transaction_id=data["user_transaction_id"],
            cardholder_id=data["cardholder_id"],
            receiver_id=data["receiver_id"],
            amount=data["amount"],
            status=TRANSACTION_NEW_STATUS
        )
        # Create an entry in the Transaction table with NEW status.
        temp_transaction_id = await self.__db.create_transaction_record(record)

        message = {
            "eventName": Events.TRANSACTION_CREATED.value,
            "messageType": MESSAGE_TYPE_REQUEST,
            "responseType": RESPONSE_SUCCESS,
            "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
            "message": "",
            "data": {
                "temp_transaction_id": str(temp_transaction_id),
                "user_transaction_id": record.user_transaction_id,
                "cardholder_id": record.cardholder_id,
                "receiver_id": record.receiver_id,
                "amount": record.amount,
                "status": record.status
            }
        }
        await wallet_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{temp_transaction_id}]. Status: {TRANSACTION_NEW_STATUS}.")

    async def execute_transaction(self, data, wallet_topic_obj):
        # Get a transaction record.
        record = await self.__db.get_transaction_record(data["temp_transaction_id"])
        # Mark a transaction as such that is waiting to be executed.
        temp_transaction_id = await self.__db.update_transaction_record(data["temp_transaction_id"],
                                                                        {"status": TRANSACTION_PENDING_STATUS})

        # Utilize data somehow.
        message = {
            "eventName": Events.TRANSACTION_PENDING.value,
            "messageType": MESSAGE_TYPE_REQUEST,
            "responseType": RESPONSE_SUCCESS,
            "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
            "message": "",
            "data": {
                "temp_transaction_id": temp_transaction_id,
                "user_transaction_id": record['user_transaction_id'],
                "cardholder_id": record["cardholder_id"],
                "receiver_id": record["receiver_id"],
                "amount": record["amount"],
                "status": record["status"]
            }
        }
        await wallet_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{temp_transaction_id}]. Status: {TRANSACTION_PENDING_STATUS}.")

    async def send_transaction_result(self, temp_transaction_id, all_results_topic_obj):
        record = await self.__db.get_transaction_record(temp_transaction_id)
        # TODO: check correctness of cardholder id on web before returning response
        message = {
            'user_transaction_id': record['user_transaction_id'],
            'cardholder_id': record['cardholder_id'],
            'receiver_id': record['receiver_id'],
            "completed": record['status'] == TRANSACTION_COMPLETED_STATUS
        }

        # Send response to SAGA.
        await all_results_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())

    async def mark_transaction_complete(self, data, all_results_topic_obj):
        # Get a transaction record.
        temp_transaction_id = await self.__db.update_transaction_record(data["temp_transaction_id"],
                                                                        {"status": TRANSACTION_COMPLETED_STATUS})
        await self.send_transaction_result(temp_transaction_id, all_results_topic_obj)

        self.__logger.info(f"Transaction: [{temp_transaction_id}]. Status: {TRANSACTION_COMPLETED_STATUS}.")

    async def mark_transaction_failed(self, data, all_results_topic_obj):
        # Get a transaction record.
        temp_transaction_id = await self.__db.update_transaction_record(data["temp_transaction_id"],
                                                                        {"status": TRANSACTION_FAILED_STATUS})
        await self.send_transaction_result(temp_transaction_id, all_results_topic_obj)

        self.__logger.info(f"Transaction: [{temp_transaction_id}]. Status: {TRANSACTION_FAILED_STATUS}.")
