import json
import uuid
import datetime

from domain_logic.__constants import *
from database.__db import WalletServiceDatabase, db, ReservedTransaction
from domain_logic.utils.__utils import get_logger


class WalletService:
    def __init__(self):
        self.__logger = get_logger(name=WALLET_TOPIC)
        # Connect to WalletServiceDB.
        self.__db = WalletServiceDatabase(db)

    async def reserve_balance(self, data, transaction_topic_obj):
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
        await transaction_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{transaction_id}]. Status: RESERVED.")

    async def process_payment(self, data, transaction_topic_obj):
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
        await transaction_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: COMPLETE.")

    async def cancel_reservation(self, data, transaction_topic_obj):
        response = self.__db.calcel_reservation(data["transaction_id"])
        if response:
            event_name = Events.TRANSACTION_CANCELLED.value
            message = "Operation success."
        else:
            event_name = Events.TRANSACTION_FAILURE.value
            message = "WalletServiceError: Failed to cancel transaction."

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
        await transaction_topic_obj.send(key=uuid.uuid1().bytes, value=json.dumps(message).encode())
        self.__logger.info(f"Transaction: [{data['transaction_id']}]. Status: CANCELLED.")
