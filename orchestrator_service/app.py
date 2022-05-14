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
from domain_logic.kafka.result_consumer import consume_results


# Create app object
app = FastAPI()


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
        return False, authorizer_response

    if 'signature' not in authorizer_response.keys():
        return False, authorizer_response

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
    return is_valid_token, msg


@app.options("/{full_path:path}")
async def options():
    return JSONResponse(status_code=status.HTTP_200_OK, headers=cors)


@app.post("/handle_transaction")
async def handle_transaction(request: Request):
    form = await request.form()
    is_valid_token, msg = await validate_token(form, request)
    if not is_valid_token:
        return JSONResponse(content={'content': msg}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    request_params = form.__dict__['_dict']
    transaction_id = str(uuid.uuid1())
    producer = ServiceProducer("ServiceProducer")

    # TODO: add web validation on transaction form. Use database.forms.TransactionForm
    message_ = {
        "eventName": Events.TRANSACTION_REQUEST.value,
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
