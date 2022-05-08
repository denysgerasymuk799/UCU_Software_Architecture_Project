import boto3
from aiokafka import AIOKafkaConsumer

from config import logger, kafka_loop
from domain_logic.__constants import *


async def consume_results():
    consumer = AIOKafkaConsumer(ALL_RESULTS_TOPIC,
                                loop=kafka_loop,
                                bootstrap_servers=[KAFKA_BROKER],
                                group_id=KAFKA_CONSUMER_GROUP)
    await consumer.start()
    try:
        async for msg in consumer:
            print(f'Consumer msg: {msg}')
            session = boto3.Session(
                aws_access_key_id=ORCHESTRATOR_USER_PUBLIC_KEY,
                aws_secret_access_key=ORCHESTRATOR_USER_SECRET_KEY,
            )

    except Exception as err:
        logger.error(f'Consume error: {err}')
    finally:
        await consumer.stop()
