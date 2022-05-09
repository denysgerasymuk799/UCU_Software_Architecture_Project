from typing import List
from typing import Optional

from flask import Request
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    def load_data(self):
        form = self.request.form
        self.username = form.get(
            "email"
        )  # since auth works on username field we are considering email as username
        self.password = form.get("password")

    def is_valid(self):
        if not self.username or not (self.username.__contains__("@")):
            self.errors.append("Email is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
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

    def load_data(self):
        form = self.request.form
        self.money_amount = form.get("money_amount")
        # self.password = form.get("password")
        print('self.money_amount -- ', self.money_amount)

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
