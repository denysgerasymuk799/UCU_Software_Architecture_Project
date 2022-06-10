from domain_logic.__constants import *
from datetime import datetime


class CardManagerOperator:
    def __init__(self, client) -> None:
        self.__client = client

    def create_card(self, card_id: int):
        query = f"""
        INSERT INTO {CARDS_TABLE} (card_id, credit_limit)
        VALUES ('{card_id}', 500);
        """
        self.__client.execute_write_query(query)

        # Save card creation time to a separate table.
        query = f"""
        INSERT INTO {USERS_UNIQUE_DAILY_TABLE} (card_id, date) 
        VALUES ('{card_id}', '{datetime.now().strftime("%Y-%m-%d")}');
        """
        self.__client.execute_write_query(query)
