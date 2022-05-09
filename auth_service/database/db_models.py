import os
import motor.motor_asyncio

from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from dotenv import load_dotenv


load_dotenv()
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"),
                                                serverSelectionTimeoutMS=60_000,
                                                tls=True, tlsAllowInvalidCertificates=True)
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
    username: str
    role: str
    disabled: bool
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    hashed_password: Optional[str] = None


class UserInDB(User):
    role: str
    hashed_password: str
    disabled: bool
    firstname: Optional[str] = None
    lastname: Optional[str] = None
