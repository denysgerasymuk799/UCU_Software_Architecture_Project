from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from database.__db import AnalyticsServiceOperator
from domain_logic.__constants import *


# Create app object.
app = FastAPI()

# Create a Database operator.
operator = AnalyticsServiceOperator()

# Initialize headers for JSONResponse.
cors = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, PUT, POST, DELETE, HEAD, OPTIONS',
    'Allow': 'POST, OPTIONS'
}


def get_user_spendings(table: str, request: Request):
    """
    Get user spendings from the database for specified date range.

    :param table: (str) - table name.
    :param request: (fastapi.Request) - request.
    :return: (JSONResponse) - response with the returned record.
    """
    # Get request parameters.
    request_params = request.query_params
    try:
        card_id, from_date, to_date = request_params["card_id"], request_params["from_date"], request_params["to_date"]
    except (ValueError, KeyError):
        return JSONResponse(
            content={"content": "Invalid request parameters."}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors
        )

    # Get user spendings.
    spendings = operator.get_user_spendings(table=table, card_id=card_id, from_date=from_date, to_date=to_date)

    # In case there is no such record.
    if not spendings:
        return JSONResponse(
            content={"content": "There is no such record."}, status_code=status.HTTP_200_OK, headers=cors
        )
    return JSONResponse(content={"spendings": spendings}, status_code=status.HTTP_200_OK, headers=cors)


@app.get("/get_spendings_by_days")
def get_spendings_by_days(request: Request):
    """
    Get user spending for specified in the request day dates.
    Request date has to have the following format: YYYY-MM-DD.

    :param request: (fastapi.Request) - request.
    :return:  (JSONResponse) - response with the returned record.
    """
    return get_user_spendings(table=TR_PREAGGREGATED_DAILY_TABLE, request=request)


@app.get("/get_spendings_by_months")
def get_spendings_by_months(request: Request):
    """
    Get user spending for specified in the request day dates.
    Request date has to have the following format: YYYY-MM-DD.

    :param request: (fastapi.Request) - request.
    :return: (JSONResponse) - response with the returned record.
    """
    return get_user_spendings(table=TR_PREAGGREGATED_MONTHLY_TABLE, request=request)


@app.get("/get_bank_statistics")
def get_spendings_by_months(request: Request):
    """
    Get bank statistics for the specified date.
    Request date has to have the following format: YYYY-MM-DD.

    :param request: (fastapi.Request) - request.
    :return: (JSONResponse) - response with the returned record.
    """
    # Get request parameters.
    request_params = request.query_params
    try:
        date = request_params["date"]
    except (ValueError, KeyError):
        return JSONResponse(
            content={"content": "Invalid request parameters."}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors
        )

    # Get bank statistics.
    stats = operator.get_bank_statistics(date=date)

    # In case there is no such record.
    if not stats[0]:
        return JSONResponse(
            content={"content": "There is no such record."}, status_code=status.HTTP_200_OK, headers=cors
        )

    content = {
        "number_transactions": stats[0],
        "number_unique_users": stats[1],
        "capital_turnover": stats[2]
    }
    return JSONResponse(content=content, status_code=status.HTTP_200_OK, headers=cors)


@app.on_event("shutdown")
def shutdown():
    print("Closing connection to AnalyticsServiceOperator database...")
    operator.shutdown()
