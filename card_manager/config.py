import os
import aiohttp
import asyncio
import logging
from dotenv import load_dotenv
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from domain_logic.__cryptographer import Cryptographer
from domain_logic.__custom_logger import CustomHandler

# Set up global constants
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")  # to get a string like this run: openssl rand -hex 32
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Password protection utils
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

# Add logic for asynchronous requests
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)

# Prepare own helper class objects
cryptographer = Cryptographer(public_key_location=os.getenv('PUBLIC_KEY_LOCATION'),
                              private_key_location=os.getenv('PRIVATE_KEY_LOCATION'))
logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())

