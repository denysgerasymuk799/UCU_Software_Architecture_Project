from domain_logic.__constants import *
from pydantic import BaseModel
from bson import ObjectId
import motor.motor_asyncio
import datetime
import time


client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.web_banking


class Transaction(BaseModel):
    cardholder_id: str
    receiver_id: str
    amount: int
    status: str
    user_transaction_id: str


class Wallet(BaseModel):
    credit_limit: int


class ReservedTransaction(BaseModel):
    wallet_id: str
    amount: int
    timestamp: datetime.datetime


class TransactionServiceDatabase:
    """
    MongoDB instance available for the TransactionService.
    """
    def __init__(self, database):
        self.__db = database

    async def get_transaction_record(self, transaction_id: str):
        record = await self.__db[TRANSACTION_TABLE].find_one({"_id": ObjectId(transaction_id)})
        return record

    async def create_transaction_record(self, transaction: Transaction):
        record = await self.__db[TRANSACTION_TABLE].insert_one(transaction.__dict__)
        return record.inserted_id

    async def update_transaction_record(self, transaction_id: str, data):
        record_filter = {"_id": ObjectId(transaction_id)}
        newvalues = {"$set": data}

        await self.__db[TRANSACTION_TABLE].update_one(record_filter, newvalues)
        return transaction_id
