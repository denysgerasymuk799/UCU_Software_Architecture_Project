import json
import faust
import logging

from domain_logic.__logger import CustomHandler
from domain_logic.card_service import CardService
from domain_logic.__constants import *


# Prepare own helper class objects
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

# Initialize card service instanse.
card_service = CardService()


@app.agent(card_service_topic)
async def process_transactions(records):
    """
    Read messages from CARD topic, process them and send response to TRANSACTION topic.

    :param records: kafka topic messages.
    """
    async for record in records:
        # Get message details.
        message = json.loads(record)
        event, source, data = message['eventName'], message['producer'], message['data']
        # Log received message.
        logger.info(f"Message received. Event: [{event}]. Source: [{source}].")

        # Do the required stuff.
        if event == Events.TRANSACTION_TOPUP.value:
            await card_service.topup_balance(data, transaction_service_topic)
        elif event == Events.TRANSACTION_CREATED.value:
            await card_service.reserve_balance(data, transaction_service_topic)
        elif event == Events.TRANSACTION_PENDING.value:
            await card_service.process_payment(data, transaction_service_topic)
        elif event == Events.RESERVATION_CANCEL.value:
            await card_service.cancel_reservation(data, transaction_service_topic)
