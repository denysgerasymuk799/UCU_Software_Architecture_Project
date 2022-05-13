from domain_logic.__constants import *
from datetime import datetime
from pydantic import BaseModel


class Transaction(BaseModel):
    transaction_id: str
    card_id: str
    receiver_card_id: str
    amount: int
    status: str
    date: str


class Card(BaseModel):
    card_id: str
    credit_limit: int


class ReservedTransaction(BaseModel):
    transaction_id: str
    card_id: str
    receiver_card_id: str
    amount: int
    date: str


class TransactionServiceOperator:
    def __init__(self, client) -> None:
        self.__client = client

    def get_transaction_record(self, transaction_id: str):
        query = f"""
        SELECT transaction_id, card_id, receiver_card_id, amount, status, date 
        FROM {TRANSACTIONS_TABLE} 
        WHERE transaction_id = '{transaction_id}';
        """

        records = list(self.__client.execute(query))
        if not records:
            return None
        return records[0]

    def create_transaction_record(self, trans: Transaction):
        # Check whether such receiver exists.
        query = f"""SELECT * FROM {CARDS_TABLE} WHERE card_id = '{trans.receiver_card_id}';"""
        records = list(self.__client.execute(query))
        if not records:
            return

        # Insert transaction record into table.
        date = datetime.utcnow().strftime("%Y-%m-%d")
        query = f"""
        INSERT INTO {TRANSACTIONS_TABLE} (transaction_id, card_id, receiver_card_id, amount, status, date)
        VALUES ('{trans.transaction_id}', '{trans.card_id}', '{trans.receiver_card_id}', {trans.amount}, '{trans.status}', '{date}');
        """
        self.__client.execute(query)

    def update_transaction_status(self, transaction_id: str, status: str):
        # Get transaction record.
        query = f"""
        SELECT card_id, date 
        FROM {TRANSACTIONS_TABLE} 
        WHERE transaction_id = '{transaction_id}';
        """
        records = list(self.__client.execute(query))
        if not records:
            return None

        # Get clustering columns values.
        card_id, date = records[0][0], records[0][1]

        # Update transaction record.
        query = f"""
        UPDATE {TRANSACTIONS_TABLE}
        SET status = '{status}'
        WHERE transaction_id = '{transaction_id}' AND card_id = '{card_id}' AND date = '{date}';
        """
        self.__client.execute(query)
