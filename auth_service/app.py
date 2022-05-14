import json
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status, Request, Response, Cookie
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from Crypto.Util.number import bytes_to_long

# Import app modules
from config import logger, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context, oauth2_scheme, cryptographer
from database.db_models import db
from database.db_models import TokenData, User
from domain_logic.auth.forms import LoginForm, NewAuthUserForm
from database.db_interaction import create_new_user, get_user


# Create app object
app = FastAPI()

cors = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS'
}


@app.options("/{full_path:path}")
async def options():
    return JSONResponse(status_code=status.HTTP_200_OK, headers=cors)


async def get_json(client, url, headers, data):
    """
    Make asynchronous GET request
    """
    async with client.get(url, headers=headers, json=data) as response:
        return await response.read()


async def post_request(client, url, headers, data):
    """
    Make asynchronous POST request
    """
    async with client.post(url, headers=headers, data=data) as response:
        return await response.read()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    print('user -- ', user)
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
            msg = f'HTTPException: {credentials_exception.detail}'
            logger.error('email is None')
            # raise credentials_exception
            logger.error(msg)
            return JSONResponse(content=msg, headers=cors, status_code=status.HTTP_401_UNAUTHORIZED)
        token_data = TokenData(email=email)
    except JWTError as err:
        msg = f'JWTError: {err}\n' + f'HTTPException: {credentials_exception.detail}'
        # TODO: add Not authorized to login page and return it in this case
        logger.error(f'JWTError: {err}')
        logger.error(f'HTTPException: {credentials_exception.detail}')
        return JSONResponse(content=msg, headers=cors, status_code=status.HTTP_401_UNAUTHORIZED)
    user = await get_user(email=token_data.email)
    if user is None:
        msg = f'HTTPException: {credentials_exception.detail}'
        logger.error('user is None')
        logger.error(msg)
        return JSONResponse(content=msg, headers=cors, status_code=status.HTTP_401_UNAUTHORIZED)
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
    # Return Response on Login page in case failed authorization
    if isinstance(current_user, JSONResponse):
        return current_user
    if current_user.disabled:
        logger.error('HTTPException: Inactive user')
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user or isinstance(user, HTTPException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.user_id}


@app.post("/insert_new_auth_user")
async def insert_new_auth_user(request: Request):
    """
    Required body parameters:
    * username: str, equal to email
    * hashed_password: str, user password
    * firstname: str, user firstname
    * lastname: str, user lastname
    * role: str, user role
    """
    print('request.json() -- ', await request.json())
    form = NewAuthUserForm(request)
    logger.info(f'Request form -- {form}')
    await form.load_data()
    form.disabled = False
    if await form.is_valid():
        try:
            new_user_id = await create_new_user(db, User(**form.__dict__))
            logger.info(f'new_auth_user_id -- {new_user_id}')

            return JSONResponse(status_code=status.HTTP_200_OK, headers=cors,
                                content={"new_auth_user_id": str(new_user_id)})
        except HTTPException as err:
            form.__dict__.get("errors").append(f'HTTPException: {err.detail}')

    logger.info(f'Request errors: {form.__dict__.get("errors")}')
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, headers=cors,
                        content={"errors": form.__dict__.get("errors")})


@app.post("/login")
async def login(request: Request):
    """
    Required body parameters:
    * username: str, equal to email
    * password: str, user password
    * authorization method 'bearer' in headers
    """
    logger.info(f'Request form -- {await request.form()}')
    form = LoginForm(request)
    logger.debug(f'form_data.username -- {form.username}')
    logger.debug(f'form_data.password -- {form.password}')
    await form.load_data()
    try:
        access_token_info = await login_for_access_token(form_data=form)
        response = JSONResponse(status_code=status.HTTP_200_OK, headers=cors, content=access_token_info)
        return response
    except HTTPException as err:
        form.__dict__.get("errors").append(f'HTTPException: {err.detail}')

    logger.info(f'Request errors: {form.__dict__.get("errors")}')
    return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, headers=cors,
                        content={"errors": form.__dict__.get("errors")})


@app.post("/authorize")
async def authorize_transaction(request: Request, current_user: User = Depends(get_current_active_user)):
    """
    Required parameters:
    * authorization method 'bearer' in headers
    """
    if isinstance(current_user, JSONResponse):
        return current_user

    request_body = await request.json()
    logger.info(f'Request -- {request_body}')
    logger.info(f'current_user.username -- {current_user.username}')

    request_body_bytes = bytes(str(request_body), 'utf-8')
    request_body['signature'] = bytes_to_long(cryptographer.sign(request_body_bytes))
    request_body['validated'] = True
    response = json.dumps(request_body)
    return Response(response, headers=cors, status_code=200)
