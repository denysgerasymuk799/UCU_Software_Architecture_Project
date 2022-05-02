import logging

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse

# Import app modules
from database.db_models import db
from database.db_models import User
from domain_logic.forms import RegistrationForm
from domain_logic.custom_logger import MyHandler


# Prepare own helper class objects
logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(MyHandler())

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
    logger.info(f'Insert a new user with the next info -- {user.__dict__}')
    new_user = await db["users"].insert_one(user.__dict__)
    return new_user.inserted_id

@app.options("/{full_path:path}")
async def options():
    return JSONResponse(status_code=status.HTTP_200_OK, headers=cors)

@app.post("/registration")
async def registration(request: Request):
    logger.info('Start POST registration')
    logger.info(f'Got request form -- {await request.form()}')
    form = RegistrationForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            form.__dict__.update(msg="Registration is Successful :)")
            new_user_id = await create_new_user(db, User(**form.__dict__))
            logger.info(f'new_user_id -- {new_user_id}')
            return JSONResponse(status_code=status.HTTP_200_OK, headers=cors, content={"new_user_id": str(new_user_id)})
        except HTTPException as err:
            form.__dict__.get("errors").append(f'HTTPException: {err.detail}')

    logger.info(form.__dict__.get("errors"))
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, headers=cors, content={"errors": form.__dict__.get("errors")})
