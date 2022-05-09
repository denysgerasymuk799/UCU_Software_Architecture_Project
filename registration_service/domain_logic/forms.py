import datetime
from typing import List
from typing import Optional

from fastapi import Request
from passlib.context import CryptContext

from domain_logic.constants import *


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegistrationForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.firstname: Optional[str] = None
        self.lastname: Optional[str] = None
        self.email: Optional[str] = None
        self.password: Optional[str] = None
        self.hashed_password: Optional[str] = None
        self.repeat_password: Optional[str] = None
        self.birthday_date: Optional[str] = None
        self.city: Optional[str] = None
        self.address: Optional[str] = None
        self.disabled: Optional[bool] = None
        self.role: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.firstname = form.get("firstname")
        self.lastname = form.get("lastname")
        self.email = form.get("email")
        self.password = form.get("password")
        self.repeat_password = form.get("repeat_password")
        self.birthday_date = form.get("birthday_date")
        self.city = form.get("city")
        self.address = form.get("address")
        self.disabled = False

    async def is_valid(self):
        if not self.firstname or not self.firstname.isalpha():
            self.errors.append("Firstname must contain alphabetic letters without digits")
        if not self.lastname or not self.lastname.isalpha():
            self.errors.append("Lastname must contain alphabetic letters without digits")
        if not self.email or not self.email.__contains__("@") or not self.email.__contains__("."):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("Valid password is required")
        if not self.repeat_password or not self.repeat_password == self.password:
            self.errors.append("Repeat password must be equal to password!")

        if self.birthday_date:
            try:
                birthday_datetime = datetime.datetime.strptime(self.birthday_date, "%d/%m/%Y")
            except ValueError:
                self.errors.append("Birthday is required and must be in the next format -- %d/%m/%Y")
        else:
            self.errors.append("Birthday is required and must be in the next format -- %d/%m/%Y")

        if not self.city:
            self.errors.append("Valid city is required")
        if not self.address or not len(self.address) >= 4:
            self.errors.append("Valid address is required")
        if self.role != SIMPLE_USER:
            self.errors.append(f"During registration user role must be {SIMPLE_USER}")
        if not self.errors:
            self.hashed_password = pwd_context.hash(self.password)
            return True
        return False
