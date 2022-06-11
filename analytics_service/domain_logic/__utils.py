import json
import pandas as pd
import datapane as dp
import plotly.express as px

from copy import copy
from datetime import datetime
from Crypto.Util.number import long_to_bytes

from config import logger, client, cryptographer, cors
from domain_logic.__constants import *


def validate_date(date: str):
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD.")


async def post_request(client, url, headers, data):
    """
    Make asynchronous POST request
    """
    async with client.post(url, headers=headers, json=data) as response:
        return await response.read()


async def validate_token(form, request, token=None):
    """
    Send request to Auth service to validate JWT token.
    After getting response, also verify if it was validated by Auth service using digital signature
    """
    # Send request to authorize user transaction
    data = copy(form.__dict__['_dict'])
    data.pop('request', None)
    data.pop('errors', None)
    data['validated'] = False
    data['signature'] = None

    request_url = AUTH_SERVICE_URL + '/authorize'
    if token:
        token = 'Bearer ' + token
    authorizer_response = await post_request(client, request_url,
                                             headers={"Authorization": token if token else request.headers['Authorization'],
                                                      "Accept": "application/json"},
                                             data=data)

    # Process response to get result
    authorizer_response = authorizer_response.decode("utf-8")
    authorizer_response = json.loads(authorizer_response)
    logger.debug(f'authorizer_response --  {authorizer_response}')
    if not isinstance(authorizer_response, dict):
        return False, authorizer_response, ''

    if 'signature' not in authorizer_response.keys():
        return False, authorizer_response, ''

    signature = long_to_bytes(authorizer_response['signature'])

    check_data = copy(data)
    check_data['validated'] = False
    check_data['signature'] = None

    # Check if user transaction is authorized
    if cryptographer.verify(bytes(str(check_data), 'utf-8'), signature):
        msg = "Transaction is verified!"
        is_valid_token = True
    else:
        msg = "Transaction is not verified, since token is invalid!"
        is_valid_token = False

    logger.info(msg)
    return is_valid_token, msg, authorizer_response['card_id']


def create_bank_stats_report(operator):
    """
    Create datapane report with 3 plots for each of general bank statistics
    """
    # Get stats for the last  months from Cassandra
    statistics = operator.get_all_bank_statistics()

    # In case there is no such record.
    if not statistics[0].date:
        return -1

    content = {
        "date": [record.date.date() for record in statistics],
        "number_transactions": [record.number_transactions for record in statistics],
        "number_unique_users": [record.number_unique_users for record in statistics],
        "capital_turnover": [record.capital_turnover for record in statistics]
    }
    df = pd.DataFrame.from_dict(content)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(by="date")
    number_transactions_fig = px.line(df, x="date", y="number_transactions")
    number_unique_users_fig = px.line(df, x="date", y="number_unique_users")
    capital_turnover_fig = px.line(df, x="date", y="capital_turnover")

    dp.Report("# Bank Statistics Report",
              "## Number of transactions for the last 3 months",
              dp.Plot(number_transactions_fig),
              "## Number of unique users for the last 3 months",
              dp.Plot(number_unique_users_fig),
              "## Capital turnover for the last 3 months",
              dp.Plot(capital_turnover_fig)
              ).save(path='./report.html')
    return 0
