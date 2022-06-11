import logging
import aiohttp
import asyncio

from domain_logic.__custom_logger import CustomHandler
from domain_logic.cryptographer import Cryptographer
from domain_logic.__constants import *

cors = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS',
    'Allow': 'POST, OPTIONS'
}

# Add logic for asynchronous requests
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)

# Prepare own helper class objects
cryptographer = Cryptographer(public_key_location=os.getenv('PUBLIC_KEY_LOCATION'),
                              private_key_location=os.getenv('PRIVATE_KEY_LOCATION'))

# Prepare own helper class objects
logger = logging.getLogger('root')
if DEBUG_MODE:
    logger.setLevel('DEBUG')
else:
    logger.setLevel('INFO')
    logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())
