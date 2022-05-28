from datetime import datetime
import uuid
import json
import aiohttp
import asyncio
from copy import copy

from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from Crypto.Util.number import long_to_bytes

# Import app modules
from config import logger
from domain_logic.__constants import *
from domain_logic.utils.cryptographer import Cryptographer
from domain_logic.kafka.service_producer import ServiceProducer
from domain_logic.kafka.result_consumer import consume_results, session

from database.__cassandra_client import CassandraClient
from database.__db import TransactionServiceOperator

# Create app object
app = FastAPI()

cassandra_client = CassandraClient(
    host=CASSANDRA_HOST,
    port=CASSANDRA_PORT,
    keyspace=CASSANDRA_KEYSPACE,
    username=AMAZOM_KEYSPACES_USERNAME,
    password=AMAZOM_KEYSPACES_PASSWORD
)
cassandra_client.connect()

asyncio.create_task(consume_results())

# Add logic for asynchronous requests
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)

# Prepare own helper class objects
cryptographer = Cryptographer(public_key_location=os.getenv('PUBLIC_KEY_LOCATION'),
                              private_key_location=os.getenv('PRIVATE_KEY_LOCATION'))

cors = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS',
    'Allow': 'POST, OPTIONS'
}


async def post_request(client, url, headers, data):
    """
    Make asynchronous POST request
    """
    async with client.post(url, headers=headers, json=data) as response:
        return await response.read()


async def validate_token(form, request):
    """
    Send request to Auth service to validate JWT token.
    After getting response, also verify if it was validated by Auth service using digital signature
    """
    # Send request to authorize user transaction
    data = copy(form.__dict__['_dict'])
    data.pop('request', None)
    data.pop('errors', None)
    data['validated'] = False
    data['signature'] = None

    request_url = AUTH_SERVICE_URL + '/authorize'
    authorizer_response = await post_request(client, request_url,
                                             headers={"Authorization": request.headers['Authorization'],
                                                      "Accept": "application/json"},
                                             data=data)

    # Process response to get result
    authorizer_response = authorizer_response.decode("utf-8")
    authorizer_response = json.loads(authorizer_response)
    logger.debug(f'authorizer_response --  {authorizer_response}')
    if not isinstance(authorizer_response, dict):
        return False, authorizer_response, ''

    if 'signature' not in authorizer_response.keys():
        return False, authorizer_response, ''

    signature = long_to_bytes(authorizer_response['signature'])

    check_data = copy(data)
    check_data['validated'] = False
    check_data['signature'] = None

    logger.debug(f'check_data -- {check_data}')

    # Check if user transaction is authorized
    if cryptographer.verify(bytes(str(check_data), 'utf-8'), signature):
        msg = "Transaction is verified!"
        is_valid_token = True
    else:
        msg = "Transaction is not verified, since token is invalid!"
        is_valid_token = False
    logger.info(msg)
    return is_valid_token, msg, authorizer_response['card_id']


@app.options("/{full_path:path}")
async def options():
    return JSONResponse(status_code=status.HTTP_200_OK, headers=cors)


@app.post("/handle_transaction")
async def handle_transaction(request: Request):
    form = await request.form()
    is_valid_token, msg, auth_card_id = await validate_token(form, request)
    if not is_valid_token:
        return JSONResponse(content={'content': msg}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    request_params = form.__dict__['_dict']

    if str(auth_card_id) != request_params['card_id']:
        return JSONResponse(content={'content': 'Wrong user sender card id'}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    transaction_id = str(uuid.uuid1())
    producer = ServiceProducer("ServiceProducer")

    if request_params["transaction_type"] == TOP_UP_ACTIVITY:
        event_name = Events.TRANSACTION_TOPUP.value
    else:
        event_name = Events.TRANSACTION_REQUEST.value

    message_ = {
        "eventName": event_name,
        "messageType": MESSAGE_TYPE_REQUEST,
        "responseType": RESPONSE_SUCCESS,
        "producer": TRANSACTION_SERVICE_PRODUCER_NAME,
        "message": "",
        "data": {
            "transaction_id": transaction_id,
            "card_id": request_params['card_id'],
            "receiver_card_id": request_params['receiver_card_id'],
            "amount": request_params['amount'],
        }
    }
    await producer.send("TransactionService", message_)
    logger.info(f'The next message is sent -- {message_}')

    return JSONResponse(content={'transaction_id': transaction_id}, status_code=status.HTTP_200_OK, headers=cors)


@app.get("/get_notifications")
async def get_notifications(request: Request):
    request_params = request.query_params
    print('request_params', request_params)

    try:
        last_transaction_id = request_params['last_transaction_id']
    except (ValueError, KeyError):
        return JSONResponse(content={'content': 'no last_transaction_id parameter'},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)
    try:
        is_valid_token, msg, auth_card_id = await validate_token(request_params, request)
    except:
        return JSONResponse(content={'content': 'unauthorized'},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)

    if not is_valid_token:
        return JSONResponse(content={'content': msg}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    date = datetime.utcnow().strftime("%Y-%m-%d")

    s3_client = session.client('s3')
    response = s3_client.list_objects_v2(
        Bucket=RESULTS_BUCKET_NAME,
        Prefix=f'{auth_card_id}/{date}'
    )
    print(f'{auth_card_id}/{date}')

    if 'Contents' not in response:
        return JSONResponse(content={'new_transactions': [], 'last_transaction_id': 'empty'}, status_code=status.HTTP_200_OK, headers=cors)

    response_sorted = sorted(response['Contents'], key=lambda a: a['LastModified'], reverse=True)

    if not last_transaction_id:
        return JSONResponse(content={'new_transactions': [], 'last_transaction_id': response_sorted[0]['Key']},
                            status_code=status.HTTP_200_OK, headers=cors)

    new_transactions = []
    for obj in response_sorted:
        print('obj["Key"]', obj["Key"], '\n')
        if obj["Key"] == last_transaction_id:
            break
        obj = s3_client.get_object(
            Bucket=RESULTS_BUCKET_NAME,
            Key=f'{obj["Key"]}'
        )
        j = json.loads(obj['Body'].read())
        new_transactions.append(j)
    print("new_transactions", len(new_transactions))
    return JSONResponse(content={'new_transactions': new_transactions, 'last_transaction_id': response_sorted[0]['Key']}, status_code=status.HTTP_200_OK, headers=cors)


@app.get("/get_balance")
async def get_balance(request: Request):
    request_params = request.query_params
    print('request_params', request_params)

    try:
        card_id = int(request_params['card_id'])
    except (ValueError, KeyError):
        return JSONResponse(content={'content': 'no card id parameter'},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)

    is_valid_token, msg, auth_card_id = await validate_token(request_params, request)

    if not is_valid_token:
        return JSONResponse(content={'content': msg}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    if auth_card_id != card_id:
        return JSONResponse(content={'content': 'Wrong user sender card id'}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    db = TransactionServiceOperator(cassandra_client)
    balance = db.get_balance(card_id)

    return JSONResponse(content={'balance': balance}, status_code=status.HTTP_200_OK, headers=cors)


@app.get("/get_transactions")
async def get_transactions(request: Request):
    request_params = request.query_params
    print('request_params', request_params)

    try:
        card_id = int(request_params['card_id'])
        start_idx = int(request_params['start_idx'])
    except (ValueError, KeyError):
        return JSONResponse(content={'content': 'no card id or no start_idx parameter'},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)

    is_valid_token, msg, auth_card_id = await validate_token(request_params, request)

    if auth_card_id != card_id:
        return JSONResponse(content={'content': 'Wrong user sender card id'}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    if not is_valid_token:
        return JSONResponse(content={'content': msg},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)

    db = TransactionServiceOperator(cassandra_client)
    transactions_raw = db.get_transactions_for_card(card_id, start_idx)
    transactions = list()
    for trans_raw in transactions_raw:
        trans = dict()
        fields = ["transaction_id", "card_id", "receiver_card_id", "amount", "status", "date"]
        for item, field in zip(trans_raw, fields):
            trans[field] = str(item)
        transactions.append(trans)
    print(transactions_raw)

    return JSONResponse(content={'transactions': transactions}, status_code=status.HTTP_200_OK, headers=cors)

