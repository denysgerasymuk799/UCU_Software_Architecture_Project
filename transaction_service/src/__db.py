from src.__constants import *
from pydantic import BaseModel
from bson import ObjectId
import motor.motor_asyncio
import asyncio
import datetime
import time


client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.web_banking


class Transaction(BaseModel):
    cardholder_id: str
    receiver_id: str
    amount: int
    status: str


class Wallet(BaseModel):
    credit_limit: int


class ReservedTransaction(BaseModel):
    wallet_id: str
    amount: int
    timestamp: datetime.datetime


class TransactionServiceDatabase:
    """
    MongoDB instanse available for the TransactionService.
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


class WalletServiceDatabase:
    """
    MongoDB instanse available for the WalletService.
    """
    def __init__(self, database):
        self.__db = database

    async def create_wallet(self, cardholder_id, wallet: Wallet):
        wallet.__dict__.update({"_id": ObjectId(cardholder_id)})
        record = await self.__db[WALLET_TABLE].insert_one(wallet.__dict__)
        return record.inserted_id

    async def get_available_cardholder_balance(self, cardholder_id):
        # Get a list of all reserved transactions.
        cursor = self.__db[RESERVED_TABLE].find({"wallet_id": cardholder_id})
        records = await cursor.to_list(length=MAX_RETURN_LENGTH)
        # Get the amount of all reserved transactions.
        cumulative_amount = sum([record["amount"] for record in records])
        # Get a wallet credit limit.
        wallet = await self.__db[WALLET_TABLE].find_one({"_id": ObjectId(cardholder_id)})
        # Available limit = Current credit limit - SUM(reserved transactions).
        return wallet["credit_limit"] - cumulative_amount

    async def reserve_transaction_amount(self, transaction_id, transaction: ReservedTransaction):
        # Check if there is enough balance.
        current_limit = await self.get_available_cardholder_balance(transaction.wallet_id)
        if current_limit - transaction.amount < 0:
            return None
        # If enough balance -> Reserve transaction.
        transaction.__dict__.update({"_id": ObjectId(transaction_id)})
        record = await self.__db[RESERVED_TABLE].insert_one(transaction.__dict__)
        return record.inserted_id

    async def execute_transaction(self, transaction_id):
        # Get the transaction that needs to be executed.
        transaction = await self.__db[RESERVED_TABLE].find_one({"_id": ObjectId(transaction_id)})
        if not transaction:
            return False
        # Get wallet instanse to carry operation on.
        wallet = await self.__db[WALLET_TABLE].find_one({"_id": ObjectId(transaction["wallet_id"])})

        # Pay out money for the transaction.
        record_filter = {"_id": ObjectId(transaction["wallet_id"])}
        newvalues = {"$set": {"credit_limit": wallet["credit_limit"] - transaction["amount"]}}
        response = await self.__db[WALLET_TABLE].update_one(record_filter, newvalues)
        # Check if balance was waived off.
        if not response:
            return False

        # Delete transaction from reserved.
        for _ in range(NUM_RETRIES):
            response = await self.calcel_reservation(transaction_id)
            if response:
                return True
            time.sleep(1)
        return response

    async def calcel_reservation(self, transaction_id):
        response = await self.__db[RESERVED_TABLE].delete_one({"_id": ObjectId(transaction_id)})
        return response.acknowledged
