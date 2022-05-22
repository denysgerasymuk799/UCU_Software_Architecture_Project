from fastapi import HTTPException

from config import logger
from domain_logic.constants import *
from database.db_models import db, UserInDB
from database.db_models import User


async def create_new_user(db, user: User):
    logger.info(f'Insert a new user in {AUTH_USERS_TABLE} with the next info -- {user.__dict__}')
    new_user = await db[AUTH_USERS_TABLE].insert_one(user.__dict__)
    return new_user.inserted_id


async def get_user(email: str):
    """
    Find user in database
    """
    user_dict = await db[AUTH_USERS_TABLE].find_one({"username": email})
    if user_dict is not None:
        logger.info(f'Found user in db: user email -- {user_dict["username"]}')
        user_dict['user_id'] = str(user_dict['_id'])
        print("user_dict", user_dict)
        print(user_dict.values())
        return UserInDB(**user_dict)

    raise HTTPException(status_code=404, detail=f"User {email} not found")
