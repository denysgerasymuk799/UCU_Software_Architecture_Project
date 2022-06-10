from dotenv import load_dotenv
import os


load_dotenv("analytics-service.env")
# ------------------- Cassandra ---------------------
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE")
AMAZOM_KEYSPACES_USERNAME = os.getenv("AMAZOM_KEYSPACES_USERNAME")
AMAZOM_KEYSPACES_PASSWORD = os.getenv("AMAZOM_KEYSPACES_PASSWORD")
CERTIFICATE_PATH = "./certificates/sf-class2-root.crt"

# ------------- Cassandra Table Names ---------------
TRANSACTIONS_TABLE = "transactions"
TRANSACTIONS_BY_CARD_TABLE = "transactions_by_card"
RESERVED_TR_TABLE = "reserved_transactions"
CARDS_TABLE = "cards"
TR_PREAGGREGATED_DAILY_TABLE = "transactions_preaggregated_daily"
TR_PREAGGREGATED_MONTHLY_TABLE = "transactions_preaggregated_monthly"
BANK_STATISTICS_DAILY_TABLE = "bank_statistics_daily"
