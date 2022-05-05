from enum import Enum
from dotenv import load_dotenv
import os


load_dotenv()
# ------------- MongoDB Connector Link --------------
MONGODB_URL = os.getenv("MONGODB_URL")
# ------------- Kafka-related Constants -------------
KAFKA_BROKER = "127.0.0.1:9092"
CONSUMER_GROUP = "tr_group"
# ------------------ Kafka Topics -------------------
TRANSACTIONS_TOPIC = "TransactionService"
WALLET_TOPIC = "WalletService"
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
# ------- MongoDB Instanse Handler Variables --------
NUM_RETRIES = 5
MAX_RETURN_LENGTH = 100


class Events(Enum):
    """
    Denotes events used inside Kafka topics for message distinction.
    """
    TRANSACTION_REQUEST = "EventTransactionRequest"
    TRANSACTION_CREATED = "EventTransactionCreated"
    RESERVATION_SUCCESS = "EventReservationSuccess"
    RESERVATION_FAILURE = "EventReservationFailure"
    RESERVATION_CANCELL = "EventReservationCancell"
    TRANSACTION_PENDING = "EventTransactionPending"
    TRANSACTION_SUCCESS = "EventTransactionSuccess"
    TRANSACTION_FAILURE = "EventTransactionFailure"
    TRANSACTION_CANCELLED = "EventTransactionCancelled"
