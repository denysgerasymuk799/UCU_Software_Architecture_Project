import json
import aiohttp
import asyncio
import logging
import pymongo

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse

# Import app modules
from database.db_models import db
from database.db_models import User, AuthUser
from domain_logic.forms import RegistrationForm
from domain_logic.custom_logger import CustomHandler
from domain_logic.constants import *

# Prepare own helper class objects
logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())

# Add logic for asynchronous requests
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)

# Create app object
app = FastAPI()

cors = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS',
    'Allow': 'POST, OPTIONS'
}


async def create_new_user(db, user: User):
    user_info = user.__dict__
    logger.info(f'Insert a new user with the following info -- {user_info}')
    new_user = await db[REGISTERED_USERS_TABLE].insert_one(user_info)
    await db[WALLET_TABLE].insert_one({'_id': new_user.inserted_id, 'username': user.email, 'credit_limit': 0})
    return new_user.inserted_id


async def allocate_card(db):
    """
    Get available card from the db, mark it as taken and return
    """
    logger.info(f'Allocating a card for the new user')
    card_dict = await db[CARDS_TABLE].find_one({"enabled": False})
    if card_dict is not None:
        card_id = card_dict["card_id"]
        logger.info(f'Found available card in db: card id -- {card_id}')
        # Mark it as taken
        result = await db[CARDS_TABLE].update_one({'card_id': card_id},
                                                  {'$set': {'enabled': True}})
        print("hey", card_id, result, card_dict)
        if result.modified_count == 1:
            return card_id
        raise ValueError("Card could not be marked as Enabled")
    raise ValueError("There are no more available cards in the system")


async def post_request(client, url, headers, data):
    """
    Make asynchronous POST request
    """
    async with client.post(url, headers=headers, json=data) as response:
        return await response.read()


@app.options("/{full_path:path}")
async def options():
    return JSONResponse(status_code=status.HTTP_200_OK, headers=cors)


@app.post("/registration")
async def registration(request: Request):
    logger.info('Start POST registration')
    logger.info(f'Got request form -- {await request.form()}')
    form = RegistrationForm(request)
    form.role = SIMPLE_USER  # assign a simple user role for registered users
    form.card_id = await allocate_card(db)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Registration is Successful :)")
            new_user_id = await create_new_user(db, User(**form.__dict__))
            logger.info(f'new_user_id -- {new_user_id}')

            # Send a new user info to Auth service
            request_url = AUTH_SERVICE_URL + '/insert_new_auth_user'
            data = AuthUser(**form.__dict__).__dict__
            data['username'] = form.email
            response = await post_request(client, request_url,
                                          headers={
                                              "Accept": "application/json"},
                                          data=data)

            # Create a card via Credit Manager
            request_url = CARD_MANAGER_URL + '/create_card'
            data = AuthUser(**form.__dict__).__dict__
            data['username'] = form.email
            data['card_id'] = form.card_id
            data['token'] = os.getenv('SECRET_TOKEN')
            response_2 = await post_request(client, request_url,
                                          headers={
                                              "Accept": "application/json"},
                                          data=data)
            # Process response to get result
            response, response_2 = response.decode("utf-8"), response_2.decode("utf-8")
            response, response_2 = json.loads(response), json.loads(response_2)
            print(f'response --  {response}, response 2 --  {response_2}')
            if 'errors' not in response.keys() and 'errors' not in response_2.keys():
                return JSONResponse(status_code=status.HTTP_200_OK, headers=cors,
                                    content={"new_user_id": str(new_user_id)})
        except HTTPException as err:
            form.__dict__.get("errors").append(f'HTTPException: {err.detail}')
        except pymongo.errors.DuplicateKeyError:
            form.__dict__.get("errors").append(f'User with this email already exists')

    logger.info(form.__dict__.get("errors"))
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, headers=cors,
                        content={"errors": form.__dict__.get("errors")})
