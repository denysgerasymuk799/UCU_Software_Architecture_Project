import json
import faust
import logging

from domain_logic.utils.custom_logger import CustomHandler
from domain_logic.wallet_service import WalletService
from domain_logic.__constants import *


# Prepare own helper class objects
logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())

app = faust.App('transaction-service',
                broker=KAFKA_BROKER,
                value_serializer='raw',
                web_host=FAUST_HOST,
                web_port=FAUST_PORT)
transaction_topic_obj = app.topic(TRANSACTIONS_TOPIC)
wallet_topic_obj = app.topic(WALLET_TOPIC)
wallet_service = WalletService()


@app.agent(wallet_topic_obj)
async def process_transactions(records):
    async for record in records:
        # Get message details.
        message = json.loads(record)
        print('message -- ', message)
        event, source, data = message['eventName'], message['producer'], message['data']
        # Log received message.
        logger.info(f"Message received. Event: [{event}]. Source: [{source}].")

        # Do the required stuff.
        if event == Events.TRANSACTION_CREATED.value:
            await wallet_service.reserve_balance(data, transaction_topic_obj)
        elif event == Events.TRANSACTION_PENDING.value:
            await wallet_service.process_payment(data, transaction_topic_obj)
        elif event == Events.RESERVATION_CANCEL.value:
            await wallet_service.cancel_reservation(data, transaction_topic_obj)

    # TODO: consumer.commit???
