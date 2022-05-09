from typing import List
from typing import Optional

from fastapi import Request
from passlib.context import CryptContext

from domain_logic.constants import *


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get(
            "username"
        )  # since auth works on username field we are considering email as username
        self.password = form.get("password")


class NewAuthUserForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.disabled: bool
        self.username: Optional[str] = None
        self.hashed_password: Optional[str] = None
        self.firstname: Optional[str] = None
        self.lastname: Optional[str] = None
        self.role: Optional[str] = None

    async def load_data(self):
        form = await self.request.json()
        self.username = form.get(
            "username"
        )  # since auth works on username field we are considering email as username
        self.hashed_password = form.get("hashed_password")
        self.firstname = form.get("firstname")
        self.lastname = form.get("lastname")
        self.role = form.get("role")

    async def is_valid(self):
        if not self.firstname or not self.firstname.isalpha():
            self.errors.append("Firstname must contain alphabetic letters without digits")
        if not self.lastname or not self.lastname.isalpha():
            self.errors.append("Lastname must contain alphabetic letters without digits")
        if not self.username or not self.username.__contains__("@") or not self.username.__contains__("."):
            self.errors.append("Username is required and must be equal to email")
        if not self.errors:
            return True
        return False
