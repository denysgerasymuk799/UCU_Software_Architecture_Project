import json
import faust
import logging

from domain_logic.utils.custom_logger import CustomHandler
from domain_logic.transaction_service import TransactionService
from domain_logic.__constants import *


# Prepare own helper class objects
logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())

# Basic configurations
app = faust.App('transaction-service',
                broker=KAFKA_BROKER,
                value_serializer='raw',
                web_host=FAUST_HOST,
                web_port=FAUST_PORT)

transaction_topic_obj = app.topic(TRANSACTIONS_TOPIC)
wallet_topic_obj = app.topic(WALLET_TOPIC)
all_results_topic_obj = app.topic(ALL_RESULTS_TOPIC)
transaction_service = TransactionService()


@app.agent(transaction_topic_obj)
async def process_transactions(records):
    async for record in records:
        message = json.loads(record)
        print('message -- ', message)

        # Get message details.
        event, source, data = message['eventName'], message['producer'], message['data']
        # Log received message.
        logger.info(f"Message received. Event: [{event}]. Source: [{source}].")

        # Do the required stuff.
        if event == Events.TRANSACTION_REQUEST.value:
            await transaction_service.create_transaction(data, wallet_topic_obj)
        elif event == Events.RESERVATION_SUCCESS.value:
            await transaction_service.execute_transaction(data, wallet_topic_obj)
        elif event == Events.TRANSACTION_SUCCESS.value:
            await transaction_service.mark_transaction_complete(data, all_results_topic_obj)
        else:
            await transaction_service.mark_transaction_failed(data, all_results_topic_obj)
            logger.info(f"Transaction: [{data['temp_transaction_id']}]. Event: [{event}]")

    # TODO: consumer.commit???
