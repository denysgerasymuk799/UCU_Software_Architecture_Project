import os
import json
import aiohttp
import asyncio
import logging
import requests
from copy import copy
from jose import JWTError, jwt
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status, Request, Response, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import Token, TokenData, User, UserInDB
from auth.forms_fastapi import LoginForm, RegistrationForm
from dotenv import load_dotenv
from Crypto.Util.number import bytes_to_long, long_to_bytes

# Import app modules
from database.db_models import db
from auth.forms_fastapi import TransactionForm
from utils.custom_logger import MyHandler
from utils.cryptographer import Cryptographer

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
logger.addHandler(MyHandler())

# Create app object
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


async def get_json(client, url, headers, data):
    """
    Make asynchronous GET request
    """
    async with client.get(url, headers=headers, json=data) as response:
        return await response.read()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(email: str):
    """
    Find user in database
    """
    user_dict = await db["users"].find_one({"email": email})
    if user_dict is not None:
        logger.info(f'Found user in db: user email -- {user_dict["email"]}')
        return UserInDB(**user_dict)

    raise HTTPException(status_code=404, detail=f"User {email} not found")


async def create_new_user(db, user: User):
    print('user.__dict__ -- ', user.__dict__)
    new_user = await db["users"].insert_one(user.__dict__)
    return new_user.inserted_id


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    logger.info("Password in verified")
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create access token, which will be verified for each action, that requires authorization
    """
    # TODO: add refresh token if needed
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Access token is created")
    return encoded_jwt


async def authorize_user(access_token):
    """
    Authorize user with access_token and existence user active record in database
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f'payload -- {payload}')
        email: str = payload.get("sub")
        if email is None:
            logger.error('email is None')
            # raise credentials_exception
            logger.error(f'HTTPException: {credentials_exception.detail}')
            return RedirectResponse(url='/login')
        token_data = TokenData(email=email)
    except JWTError as err:
        # TODO: add Not authorized to login page and return it in this case
        logger.error(f'JWTError: {err}')
        logger.error(f'HTTPException: {credentials_exception.detail}')
        return RedirectResponse(url='/login')
    user = await get_user(email=token_data.email)
    if user is None:
        logger.error('user is None')
        logger.error(f'HTTPException: {credentials_exception.detail}')
        return RedirectResponse(url='/login')
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Check user access token, if it is still valid, find user in db and return it
    """
    return await authorize_user(token)


async def authorize_user_action(access_token: Optional[str] = Cookie(None)):
    """
    Check user access token, if it is still valid, find user in db and return it
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Get token value without "Bearer " prefix
        access_token = access_token[access_token.find("Bearer ") + 7:]
    except Exception as err:
        logger.error(f'Exception: {err}')
        raise credentials_exception
    return await authorize_user(access_token)


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        logger.error('HTTPException: Inactive user')
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/")
async def home_page(request: Request):
    return RedirectResponse(url='/login')


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    # response.set_cookie(key="access_token", value=f"Bearer {access_token}",
    #                     httponly=True)  # set HttpOnly cookie in response
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/registration")
def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})


@app.post("/registration")
async def registration(request: Request):
    print('start POST registration')
    print(await request.form())
    form = RegistrationForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Registration is Successful :)")
            new_user_id = await create_new_user(db, User(**form.__dict__))
            print('new_user -- ', new_user_id)
            print('type(new_user_id) -- ', type(new_user_id))

            # response = json.dumps({"new_user_id": str(new_user_id)})
            # return Response(response, status_code=status.HTTP_201_CREATED)
            return JSONResponse(status_code=status.HTTP_201_CREATED, content={"new_user_id": str(new_user_id)})
        except HTTPException as err:
            form.__dict__.get("errors").append(f'HTTPException: {err.detail}')

    logger.info(form.__dict__.get("errors"))
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"errors": form.__dict__.get("errors")})


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    print('request -- ', request.form())
    form = LoginForm(request)
    await form.load_data()
    try:
        access_token_info = await login_for_access_token(form_data=form)
        response = JSONResponse(status_code=status.HTTP_302_FOUND, content=access_token_info)
        return response
    except HTTPException as err:
        form.__dict__.get("errors").append(f'HTTPException: {err.detail}')

    logger.info(form.__dict__.get("errors"))
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"errors": form.__dict__.get("errors")})


@app.get("/profile_page")
def profile_page(request: Request, authorize_response: User = Depends(authorize_user_action)):
    # Return RedirectResponse on Login page in case failed authorization
    if isinstance(authorize_response, RedirectResponse):
        return authorize_response
    logger.info(f'current_user.email -- {authorize_response.email}')
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/transactions/handle_transaction")
async def handle_transaction(request: Request, authorize_response: User = Depends(authorize_user_action),
                             access_token: Optional[str] = Cookie(None)):
    # Return RedirectResponse on Login page in case failed authorization
    if isinstance(authorize_response, RedirectResponse):
        return authorize_response
    logger.info(f'current_user.email -- {authorize_response.email}')

    form = TransactionForm(request)
    form.card_from = "4444444444444444"
    form.card_from_cvv = "123"
    form.card_from_exp_date_month = "12"
    form.card_from_exp_date_year = "24"
    form.card_to = "5555555555555555"

    await form.load_data()
    if form.is_valid():
        host = request.client.host
        port = request.client.port
        get_test_url = f"http://{host}:8000/transactions/authorize"

        # Send request to authorize user transaction
        data = copy(form.__dict__)
        data.pop('request', None)
        data.pop('errors', None)
        data['validated'] = False
        data['signature'] = None
        authorizer_response = await get_json(client, get_test_url,
                                             headers={"Authorization": access_token, "Accept": "application/json"},
                                             data=data)

        # Process response to get result
        authorizer_response = authorizer_response.decode("utf-8")
        authorizer_response = json.loads(authorizer_response)
        signature = long_to_bytes(authorizer_response['signature'])

        check_data = copy(data)
        check_data['validated'] = False
        check_data['signature'] = None

        # Check if user transaction is authorized
        if cryptographer.verify(bytes(str(check_data), 'utf-8'), signature):
            msg = "Transaction is verified!"
        else:
            msg = "Transaction is not verified!"
        logger.info(msg)
        return Response(msg, status_code=200)


@app.get("/transactions/authorize")
async def authorize_transaction(request: Request, current_user: User = Depends(get_current_active_user)):
    request_body = await request.json()
    logger.info(f'Request -- {request_body}')
    logger.info(f'current_user.email -- {current_user.email}')

    request_body_bytes = bytes(str(request_body), 'utf-8')
    request_body['signature'] = bytes_to_long(cryptographer.sign(request_body_bytes))
    request_body['validated'] = True
    response = json.dumps(request_body)
    return Response(response, status_code=200)
