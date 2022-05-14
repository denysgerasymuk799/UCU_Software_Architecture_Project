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


class CardServiceOperator:
    def __init__(self, client) -> None:
        self.__client = client

    def create_card(self, card_id):
        query = f"""
        INSERT INTO {CARDS_TABLE} (card_id, credit_limit)
        VALUES ('{card_id}', 0);
        """
        return self.__client.execute_write_query(query)

    def topup_balance(self, card_id: str, amount: int):
        # Get cardholder current credit limit to carry operation on.
        query = f"""SELECT credit_limit FROM {CARDS_TABLE} WHERE card_id = '{card_id}';"""
        try:
            cardholder_credit_limit = list(self.__client.execute_read_query(query))[0][0]
        except IndexError:
            return None

        query = f"""
        UPDATE {CARDS_TABLE}
        SET credit_limit = {cardholder_credit_limit + amount}
        WHERE card_id = '{card_id}';
        """
        self.__client.execute_write_query(query)
        return True

    def get_available_card_balance(self, card_id: str):
        # Get an amount of all reserved transactions.
        query = f"""SELECT amount FROM {RESERVED_TR_TABLE} WHERE card_id = '{card_id}';"""
        reserved_amount = sum(row[0] for row in list(self.__client.execute_read_query(query)))

        # Get an available card credit limit.
        query = f"""SELECT credit_limit FROM {CARDS_TABLE} WHERE card_id = '{card_id}';"""
        credit_limit = list(self.__client.execute_read_query(query))[0][0]
        # Available limit = Current credit limit - SUM(reserved transactions).
        return credit_limit - reserved_amount

    def reserve_transaction_amount(self, trans: ReservedTransaction):
        # Check if there is enough balance.
        current_limit = self.get_available_card_balance(trans.card_id)
        if current_limit - trans.amount < 0:
            return None

        # If enough balance -> Reserve transaction.
        query = f"""
        INSERT INTO {RESERVED_TR_TABLE} (transaction_id, card_id, receiver_card_id, amount, date)
        VALUES ('{trans.transaction_id}', '{trans.card_id}', '{trans.receiver_card_id}', {trans.amount}, '{trans.date}');
        """
        self.__client.execute_write_query(query)

        query = f"""
        SELECT transaction_id FROM {RESERVED_TR_TABLE} 
        WHERE card_id = '{trans.card_id}' AND transaction_id = '{trans.transaction_id}';
        """
        records = list(self.__client.execute_read_query(query))
        if not records:
            return None
        return records[0][0]

    def execute_transaction(self, card_id: str, transaction_id: str):
        # Get the transaction that needs to be executed.
        query = f"""
        SELECT transaction_id, card_id, receiver_card_id, amount, date 
        FROM {RESERVED_TR_TABLE} 
        WHERE card_id = '{card_id}' AND transaction_id = '{transaction_id}';
        """

        transactions = list(self.__client.execute_read_query(query))
        if not transactions:
            return None
        else:
            print(transactions[0][4])
            transaction = Transaction(
                transaction_id=transactions[0][0],
                card_id=transactions[0][1],
                receiver_card_id=transactions[0][2],
                amount=transactions[0][3],
                status="",
                date=str(transactions[0][4])
            )

        # Get cardholder current credit limit to carry operation on.
        query = f"""SELECT credit_limit FROM {CARDS_TABLE} WHERE card_id = '{transaction.card_id}';"""
        try:
            cardholder_credit_limit = list(self.__client.execute_read_query(query))[0][0]
        except IndexError:
            return None

        # Get receiver current credit limit.
        query = f"""SELECT credit_limit FROM {CARDS_TABLE} WHERE card_id = '{transaction.receiver_card_id}';"""
        try:
            receiver_credit_limit = list(self.__client.execute_read_query(query))[0][0]
        except IndexError:
            return None

        # Withdraw money from the cardholder card.
        # Deposit money to the receiver card.
        query = f"""
        UPDATE {CARDS_TABLE}
        SET credit_limit = {cardholder_credit_limit - transaction.amount}
        WHERE card_id = '{transaction.card_id}';
        """
        self.__client.execute_write_query(query)

        query = f"""
        UPDATE {CARDS_TABLE}
        SET credit_limit = {receiver_credit_limit + transaction.amount}
        WHERE card_id = '{transaction.receiver_card_id}';
        """
        self.__client.execute_write_query(query)

        # Send transaction to preaggregation.
        transaction_datetime = datetime.strptime(transaction.date, "%Y-%m-%d")
        monthly_date = datetime(year=transaction_datetime.year, month=transaction_datetime.month, day=1)

        self.update_card_statistics(TR_PREAGGREGATED_DAILY_TABLE, transaction.date, transaction)
        self.update_card_statistics(TR_PREAGGREGATED_MONTHLY_TABLE, monthly_date.strftime("%Y-%m-%d"), transaction)

        # Cancel reservation.
        self.cancel_reservation(transaction.card_id, transaction.transaction_id)
        return True

    def update_card_statistics(self, table: str, date: str, transaction: Transaction):
        # Check if there were successful transactions on that day.
        query = f"""
        SELECT card_id, total_amount FROM {table} 
        WHERE card_id = '{transaction.card_id}' AND date = '{date}';
        """
        records = list(self.__client.execute_read_query(query))

        if not records:
            # If this is the first transaction over a day, insert the record.
            query = f"""
            INSERT INTO {table} (card_id, total_amount, date)
            VALUES ('{transaction.card_id}', {transaction.amount}, '{date}');
            """
        else:
            # Else, update the total daily amount spent.
            total_amount = records[0][1]
            query = f"""
            UPDATE {table}
            SET total_amount = {total_amount + transaction.amount}
            WHERE card_id = '{transaction.card_id}' AND date = '{date}';
            """
        self.__client.execute_write_query(query)

    def cancel_reservation(self, card_id: str, transaction_id: str):
        query = f"""
        DELETE FROM {RESERVED_TR_TABLE} 
        WHERE card_id = '{card_id}' AND transaction_id = '{transaction_id}';
        """
        self.__client.execute_write_query(query)
