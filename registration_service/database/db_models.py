import os
import motor.motor_asyncio

from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from dotenv import load_dotenv


load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
db = client.web_banking


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    hashed_password: Optional[str] = None
    birthday_date: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
