from database.__cassandra_client import CassandraClient
from domain_logic.__constants import *
from domain_logic.__utils import validate_date


class AnalyticsServiceOperator:
    def __init__(self):
        self.__client = CassandraClient(
            host=CASSANDRA_HOST,
            port=CASSANDRA_PORT,
            keyspace=CASSANDRA_KEYSPACE,
            username=AMAZOM_KEYSPACES_USERNAME,
            password=AMAZOM_KEYSPACES_PASSWORD
        )
        self.__client.connect()

    def get_user_spendings(self, table: str, card_id: str, from_date: str, to_date: str):
        # Validate date format to prevent SQL injections.
        validate_date(from_date)
        validate_date(to_date)

        query = f"""
        SELECT total_amount FROM {table}
        WHERE card_id = '{card_id}' AND date >= '{from_date}' AND  date <= '{to_date}';
        """
        # In case there are no records.
        try:
            spendings = sum(row[0] for row in list(self.__client.execute_read_query(query)))
            return spendings
        except IndexError:
            return None

    def get_bank_statistics(self, date: str):
        # Validate date format to prevent SQL injections.
        validate_date(date)

        # Get statistics for a certain date.
        query = f"""
        SELECT number_transactions, number_unique_users, capital_turnover
        FROM {BANK_STATISTICS_DAILY_TABLE}
        WHERE date = '{date}';
        """
        # In case there are no records.
        try:
            statistics = list(self.__client.execute_read_query(query))[0]
            return statistics.number_transactions, statistics.number_unique_users, statistics.capital_turnover
        except IndexError:
            return None, None, None

    def get_all_bank_statistics(self):
        # Get statistics for a certain date.
        query = f"""
        SELECT "date", number_transactions, number_unique_users, capital_turnover
        FROM {BANK_STATISTICS_DAILY_TABLE}
        LIMIT 92;
        """
        # In case there are no records.
        try:
            statistics = list(self.__client.execute_read_query(query))
            return statistics
        except IndexError:
            return None, None, None

    def shutdown(self):
        self.__client.close()
