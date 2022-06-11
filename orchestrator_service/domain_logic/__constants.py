import os
from enum import Enum
from dotenv import load_dotenv


load_dotenv()
# ------------- Constants to setup --------------
DEBUG_MODE = False
GENERATOR_TOKEN = os.getenv("GENERATOR_TOKEN")
# ------------- Service Links --------------
MONGODB_URL = os.getenv("MONGODB_URL")
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
KAFKA_CONFIG_FILE = os.getenv("KAFKA_CONFIG_FILE")
# ------------- Kafka-related Constants -------------
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
CONSUMER_GROUP = "tr_group"
# ------------------ Kafka Topics -------------------
TRANSACTIONS_TOPIC = "TransactionService"
WALLET_TOPIC = "WalletService"
ALL_RESULTS_TOPIC = "ResultsTopic"
KAFKA_CONSUMER_GROUP = "result_consumer_group"
# ------------- S3 Credentials --------------
ORCHESTRATOR_USER_PUBLIC_KEY = os.getenv("ORCHESTRATOR_USER_PUBLIC_KEY")
ORCHESTRATOR_USER_SECRET_KEY = os.getenv("ORCHESTRATOR_USER_SECRET_KEY")
RESULTS_BUCKET_NAME = os.getenv("RESULTS_BUCKET_NAME")
# ------------- Message Body Variables --------------
RESPONSE_SUCCESS = 200
MESSAGE_TYPE_RESPONSE = "Response"
MESSAGE_TYPE_REQUEST = "Request"
# ---------------- Logger Constants -----------------
LOGS_PATH = "../logs/"
WALLET_SERVICE_PRODUCER_NAME = "WalletServiceProducer"
TRANSACTION_SERVICE_PRODUCER_NAME = "TransactionServiceProducer"
# ----------------- DB Table Names ------------------
TRANSACTION_TABLE = "transactions"
RESERVED_TABLE = "reserved"
WALLET_TABLE = "wallet"
# ------- MongoDB Instance Handler Variables --------
NUM_RETRIES = 5
MAX_RETURN_LENGTH = 100

# ------------------- Cassandra ---------------------
CASSANDRA_HOST = os.getenv("CASSANDRA_HOST")
CASSANDRA_PORT = int(os.getenv("CASSANDRA_PORT"))
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE")
AMAZOM_KEYSPACES_USERNAME = os.getenv("AMAZOM_KEYSPACES_USERNAME")
AMAZOM_KEYSPACES_PASSWORD = os.getenv("AMAZOM_KEYSPACES_PASSWORD")
CERTIFICATE_PATH = "certificates/sf-class2-root.crt"

# ------------- Cassandra Table Names ---------------
TRANSACTIONS_TABLE = "transactions"
TRANSACTIONS_BY_CARD_TABLE = "transactions_by_card"
RESERVED_TR_TABLE = "reserved_transactions"
CARDS_TABLE = "cards"
TR_PREAGGREGATED_DAILY_TABLE = "transactions_preaggregated_daily"
TR_PREAGGREGATED_MONTHLY_TABLE = "transactions_preaggregated_monthly"

TOP_UP_ACTIVITY = "BALANCE-TOP-UP"
TRANSACTION_ACTIVITY = "TRANSACTION"


class Events(Enum):
    """
    Denotes events used inside Kafka topics for message distinction.
    """
    TRANSACTION_TOPUP = "EventTransactionTopUp"
    TRANSACTION_REQUEST = "EventTransactionRequest"
    TRANSACTION_CREATED = "EventTransactionCreated"
    RESERVATION_SUCCESS = "EventReservationSuccess"
    RESERVATION_FAILURE = "EventReservationFailure"
    RESERVATION_CANCELL = "EventReservationCancell"
    TRANSACTION_PENDING = "EventTransactionPending"
    TRANSACTION_SUCCESS = "EventTransactionSuccess"
    TRANSACTION_FAILURE = "EventTransactionFailure"
    TRANSACTION_CANCELLED = "EventTransactionCancelled"
