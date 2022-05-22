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

    def get_balance(self, card_id: int):
        credit_limit_query = f"""
                        SELECT credit_limit
                        FROM {CARDS_TABLE} 
                        WHERE card_id = '{card_id}';
                        """
        credit_limit = list(self.__client.execute_read_query(credit_limit_query))
        if credit_limit:
            credit_limit = credit_limit[0][0]
        else:
            credit_limit = 0

        reserved_query = f"""
                SELECT amount 
                FROM {RESERVED_TR_TABLE} 
                WHERE card_id = '{card_id}';
                """
        reserved_sum = list(self.__client.execute_read_query(reserved_query))
        if reserved_sum:
            sum_money = 0
            for val in reserved_sum:
                sum_money += val[0]
        else:
            sum_money = 0

        return credit_limit - sum_money

    def get_transactions_for_card(self, card_id: int, start_idx: int):
        query = f"""
                SELECT transaction_id, sender_card_id, receiver_card_id, amount, status, toUnixTimestamp(date) 
                FROM {TRANSACTIONS_BY_CARD_TABLE} 
                WHERE card_id = '{card_id}';
                """

        records = list(self.__client.execute_read_query(query))
        max_idx = len(records)

        if start_idx > max_idx - 1:
            return []
        if not records:
            return None

        return records[start_idx:min(start_idx+10, max_idx)]
