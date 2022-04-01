import datetime
from typing import List
from typing import Optional

from fastapi import Request
from passlib.context import CryptContext


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
            "email"
        )  # since auth works on username field we are considering email as username
        self.password = form.get("password")


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
        if not self.errors:
            self.hashed_password = pwd_context.hash(self.password)
            return True
        return False


class TransactionForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.card_from: Optional[str] = None
        self.card_from_cvv: Optional[str] = None
        self.card_from_exp_date_month: Optional[str] = None
        self.card_from_exp_date_year: Optional[str] = None
        self.card_to: Optional[str] = None
        self.money_amount: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.card_from = form.get("card_from")
        self.card_from_cvv = form.get("card_from_cvv")
        self.card_from_exp_date_month = form.get("card_from_exp_date_month")
        self.card_from_exp_date_year = form.get("card_from_exp_date_year")
        self.card_to = form.get("card_to")
        self.money_amount = form.get("money_amount")

    def is_valid(self):
        if not self.card_from or not self.card_from.isdigit() or not len(self.card_from) == 16:
            self.errors.append("Card from is required and should contain 16 digits")
        if not self.card_to or not self.card_to.isdigit() or not len(self.card_to) == 16:
            self.errors.append("Card to is required and should contain 16 digits")
        if not self.card_from_cvv or not self.card_from_cvv.isdigit() or not len(self.card_from_cvv) == 3:
            self.errors.append("Card from cvv is required and should contain 3 digits")
        if not self.card_from_exp_date_month or not self.card_from_exp_date_month.isdigit() \
                or not len(self.card_from_exp_date_month) == 2\
                or not self.card_from_exp_date_year or not self.card_from_exp_date_year.isdigit() \
                or not len(self.card_from_exp_date_year) == 2:
            self.errors.append("Card from expiration date is required and should contain month and year")
        if not self.money_amount or not self.money_amount.isdigit() or not int(self.money_amount) >= 5:
            self.errors.append("Money amount is required and should be greater than 5")
        if not self.errors:
            return True
        return False
