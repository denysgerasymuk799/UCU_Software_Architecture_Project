from domain_logic.__constants import *


class CardManagerOperator:
    def __init__(self, client) -> None:
        self.__client = client

    def create_card(self, card_id: int):
        query = f"""
        INSERT INTO {CARDS_TABLE} (card_id, credit_limit)
        VALUES ('{card_id}', 0);
        """
        self.__client.execute_write_query(query)
