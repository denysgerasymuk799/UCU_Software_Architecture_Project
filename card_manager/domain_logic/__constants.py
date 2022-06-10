from enum import Enum
from dotenv import load_dotenv
import os


load_dotenv()
# ----------------- Service Links -------------------
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")

# ------------- Faust-related Constants -------------
FAUST_HOST = os.getenv("FAUST_HOST")
FAUST_PORT = "8007"

# ------------- Kafka-related Constants -------------
KAFKA_BROKER = os.getenv("KAFKA_BROKER")
TRANSACTIONS_TOPIC = "TransactionService"
CARD_TOPIC = "CardService"
ALL_RESULTS_TOPIC = "AllResultsTopic"

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
USERS_UNIQUE_DAILY_TABLE = "unique_users_daily"

# ------------- Message Body Variables --------------
RESPONSE_SUCCESS = 200
MESSAGE_TYPE_RESPONSE = "Response"
MESSAGE_TYPE_REQUEST = "Request"
TRANSACTION_NEW_STATUS = "NEW"
TRANSACTION_PENDING_STATUS = "PENDING"
TRANSACTION_COMPLETED_STATUS = "COMPLETED"
TRANSACTION_FAILED_STATUS = "FAILED"

# ---------------- Logger Constants -----------------
LOGS_PATH = "../logs/"
CARD_SERVICE_PRODUCER_NAME = "CardServiceProducer"
TRANSACTION_SERVICE_PRODUCER_NAME = "TransactionServiceProducer"

TOP_UP_ACTIVITY = "BALANCE-TOP-UP"


class Events(Enum):
    """
    Denotes events used inside Kafka topics for message distinction.
    """
    TRANSACTION_TOPUP = "EventTransactionTopUp"
    TRANSACTION_REQUEST = "EventTransactionRequest"
    TRANSACTION_CREATED = "EventTransactionCreated"
    RESERVATION_SUCCESS = "EventReservationSuccess"
    RESERVATION_FAILURE = "EventReservationFailure"
    RESERVATION_CANCEL = "EventReservationCancel"
    TRANSACTION_PENDING = "EventTransactionPending"
    TRANSACTION_SUCCESS = "EventTransactionSuccess"
    TRANSACTION_FAILURE = "EventTransactionFailure"
    TRANSACTION_CANCELLED = "EventTransactionCancelled"
