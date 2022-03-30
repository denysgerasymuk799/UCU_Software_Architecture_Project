from pydantic import BaseModel
from typing import Optional


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
