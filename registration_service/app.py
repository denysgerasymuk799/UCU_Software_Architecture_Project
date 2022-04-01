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


async def create_new_user(db, user: User):
    print('user.__dict__ -- ', user.__dict__)
    new_user = await db["users"].insert_one(user.__dict__)
    return new_user.inserted_id


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
