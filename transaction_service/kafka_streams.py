from domain_logic.__logger import CustomHandler
from domain_logic.transaction_service import TransactionService
from domain_logic.__constants import *

import json
import faust
import logging


# Prepare own helper class objects.
logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())

# Initialize Faust app along with Kafka topic objects.
app = faust.App('transaction-service',
                broker=KAFKA_BROKER,
                value_serializer='raw',
                web_host=FAUST_HOST,
                web_port=FAUST_PORT)
transaction_service_topic = app.topic(TRANSACTIONS_TOPIC)
card_service_topic = app.topic(CARD_TOPIC)
results_topic = app.topic(ALL_RESULTS_TOPIC)

# Initialize transaction service instanse.
transaction_service = TransactionService()


@app.agent(transaction_service_topic)
async def process_transactions(records):
    async for record in records:
        # Get message details.
        message = json.loads(record)
        event, source, data = message['eventName'], message['producer'], message['data']
        # Log received message.
        logger.info(f"Message received. Event: [{event}]. Source: [{source}].")

        # Do the required stuff.
        if event == Events.TRANSACTION_TOPUP.value:
            await transaction_service.create_topup_transaction(data, card_service_topic)
        elif event == Events.TRANSACTION_REQUEST.value:
            await transaction_service.create_transaction(data, card_service_topic)
        elif event == Events.RESERVATION_SUCCESS.value:
            await transaction_service.execute_transaction(data, card_service_topic)
        elif event == Events.TRANSACTION_SUCCESS.value:
            await transaction_service.set_transaction_completion_status(data, TRANSACTION_COMPLETED_STATUS, results_topic)
        else:
            await transaction_service.set_transaction_completion_status(data, TRANSACTION_FAILED_STATUS, results_topic)
            logger.info(f"Transaction: [{data['transaction_id']}]. Event: [{event}]")
