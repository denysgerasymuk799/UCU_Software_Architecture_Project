import json
import aiohttp
import asyncio
import logging
from copy import copy

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from Crypto.Util.number import bytes_to_long, long_to_bytes

# Import app modules
from domain_logic.utils.custom_logger import CustomHandler
from domain_logic.__constants import *
from domain_logic.utils.cryptographer import Cryptographer


# Prepare own helper class objects
logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())

# Add logic for asynchronous requests
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)

# Prepare own helper class objects
cryptographer = Cryptographer(public_key_location=os.getenv('PUBLIC_KEY_LOCATION'),
                              private_key_location=os.getenv('PRIVATE_KEY_LOCATION'))

# Create app object
app = FastAPI()

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


@app.options("/{full_path:path}")
async def options():
    return JSONResponse(status_code=status.HTTP_200_OK, headers=cors)


@app.post("/handle_transaction")
async def handle_transaction(request: Request):
    form = await request.form()

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
    print(f'authorizer_response --  {authorizer_response}')
    signature = long_to_bytes(authorizer_response['signature'])

    check_data = copy(data)
    check_data['validated'] = False
    check_data['signature'] = None

    print('check_data -- ', check_data)
    content_to_hash = ''
    for key in ['card_from', 'card_from_cvv', 'card_from_exp_date_month',
                'card_from_exp_date_year', 'card_to', 'money_amount']:
        content_to_hash += check_data[key]

    # Check if user transaction is authorized
    if cryptographer.verify(bytes(str(content_to_hash), 'utf-8'), signature):
        msg = "Transaction is verified!"
    else:
        msg = "Transaction is not verified!"
    logger.info(msg)
    return JSONResponse(content={'content': msg}, status_code=status.HTTP_200_OK, headers=cors)