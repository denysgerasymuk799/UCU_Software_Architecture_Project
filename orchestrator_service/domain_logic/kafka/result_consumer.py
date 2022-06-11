import json
import boto3
from aiokafka import AIOKafkaConsumer

from config import logger, kafka_loop
from domain_logic.__constants import *
from datetime import datetime


session = boto3.Session(
    aws_access_key_id=ORCHESTRATOR_USER_PUBLIC_KEY,
    aws_secret_access_key=ORCHESTRATOR_USER_SECRET_KEY,
    region_name='eu-central-1'
)
s3_client = session.resource('s3')


async def consume_results():
    consumer = AIOKafkaConsumer(ALL_RESULTS_TOPIC,
                                loop=kafka_loop,
                                bootstrap_servers=[KAFKA_BROKER],
                                group_id=KAFKA_CONSUMER_GROUP,
                                auto_offset_reset="latest")
    await consumer.start()
    try:
        async for record in consumer:
            print(f'Consumer record: {record}')
            msg = json.loads(record.value)
            transaction_id = msg['transaction_id']
            card_id = msg['card_id']
            receiver_card_id = msg['receiver_card_id']
            date = datetime.utcnow().strftime("%Y-%m-%d")
            # Add transaction id into json file name
            s3object = s3_client.Object(RESULTS_BUCKET_NAME, f'{card_id}/{date}/{transaction_id}.json')
            res = s3object.put(
                Body=(bytes(json.dumps(msg).encode('UTF-8')))
            )
            print("Record put into S3", res)
            if receiver_card_id != TOP_UP_ACTIVITY:
                s3object = s3_client.Object(RESULTS_BUCKET_NAME, f'{receiver_card_id}/{date}/{transaction_id}.json')
                s3object.put(
                    Body=(bytes(json.dumps(msg).encode('UTF-8')))
                )
            await consumer.commit()
    except Exception as err:
        logger.error(f'Consume error: {err}')
    finally:
        await consumer.stop()
