import json
import boto3
from aiokafka import AIOKafkaConsumer

from config import logger, kafka_loop
from domain_logic.__constants import *


session = boto3.Session(
    aws_access_key_id=ORCHESTRATOR_USER_PUBLIC_KEY,
    aws_secret_access_key=ORCHESTRATOR_USER_SECRET_KEY,
)
s3_client = session.resource('s3')


async def consume_results():
    consumer = AIOKafkaConsumer(ALL_RESULTS_TOPIC,
                                loop=kafka_loop,
                                bootstrap_servers=[KAFKA_BROKER],
                                group_id=KAFKA_CONSUMER_GROUP)
    await consumer.start()
    try:
        async for record in consumer:
            print(f'Consumer record: {record}')
            msg = json.loads(record.value)
            print(f'Consumer msg: {msg}')
            user_transaction_id = msg['user_transaction_id']
            # TODO: add transaction id into json file name
            s3object = s3_client.Object(RESULTS_BUCKET_NAME, f'{user_transaction_id}.json')

            s3object.put(
                Body=(bytes(json.dumps(msg).encode('UTF-8')))
            )

    except Exception as err:
        logger.error(f'Consume error: {err}')
    finally:
        await consumer.stop()
