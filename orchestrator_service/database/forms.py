from typing import List
from typing import Optional

from fastapi import Request


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
