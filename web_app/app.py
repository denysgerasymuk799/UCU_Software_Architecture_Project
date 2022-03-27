import os
import requests
from jose import JWTError, jwt
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import Token, TokenData, User, UserInDB
from auth.forms import LoginForm
from dotenv import load_dotenv

# import app modules
from database.db_models import db
from domain_logic.transactions import TransactionForm

# to get a string like this run:
# openssl rand -hex 32
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(email: str):
    user_dict = await db["users"].find_one({"email": email})
    if user_dict is not None:
        print('user_dict -- ', user_dict)
        return UserInDB(**user_dict)

    raise HTTPException(status_code=404, detail=f"User {email} not found")


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    print('get_current_user(): token -- ', token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print('payload -- ', payload)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await get_user(email=token_data.email)
    print('user -- ', user)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    print('get_current_active_user(): current_user -- ', current_user)
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/")
async def home_page(request: Request):
    return RedirectResponse(url='/login')


@app.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
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
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)  # set HttpOnly cookie in response
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items")
# async def read_own_items(current_user: User = Depends(get_current_active_user)):
async def read_own_items(access_token: Optional[str] = Cookie(None)):
    print('read_own_items: access_token -- ', access_token)
    token = access_token[access_token.find("Bearer ") + 1:]
    print('token -- ', token)
    current_user = await get_current_active_user(token)
    return [{"item_id": "Foo", "owner": current_user.email}]


@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Login Successful :)")
            # response = templates.TemplateResponse("index.html", form.__dict__)
            response = RedirectResponse(url='/profile_page',
                                        status_code=status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form)
            print('response.raw_headers -- ', response.raw_headers)
            return response
        except HTTPException:
            pass

    form.__dict__.update(msg="")
    form.__dict__.get("errors").append("Incorrect Email or Password")
    return templates.TemplateResponse("login.html", form.__dict__)


@app.get("/profile_page")
def profile_page(request: Request, access_token: Optional[str] = Cookie(None)):
    print('profile_page(): access_token -- ', access_token)
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/transactions/handle_transaction")
async def handle_transaction(request: Request, access_token: Optional[str] = Cookie(None)):
    form = TransactionForm(request)
    form.card_from = "4444444444444444"
    form.card_from_cvv = "123"
    form.card_from_exp_date_month = "12"
    form.card_from_exp_date_year = "24"
    form.card_to = "5555555555555555"

    await form.load_data()
    if form.is_valid():
        print("Validate transaction: form.__dict__ -- ", form.__dict__)
        host = request.client.host
        port = request.client.port
        get_test_url = f"http://{host}:8000/transactions/authorize"
        print('get_test_url -- ', get_test_url)
        print('access_token -- ', access_token)

        test_get_response = requests.get(get_test_url, headers={"Authorization": access_token,
                                                                "Accept": "application/json"})
        print('test_get_response -- ', test_get_response.text)


@app.get("/transactions/authorize")
async def authorize_transaction(current_user: User = Depends(get_current_active_user)):
# async def authorize_transaction(access_token: Optional[str] = Cookie(None)):
#     print('access_token -- ', access_token)
    print('authorize_transaction: current_user -- ', current_user)
    return Response("Authorized", status_code=200)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8080)
