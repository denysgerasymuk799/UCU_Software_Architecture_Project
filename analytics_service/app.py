from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse, HTMLResponse

from config import logger
from database.__db import AnalyticsServiceOperator
from domain_logic.__constants import *
from domain_logic.__utils import validate_token, create_bank_stats_report


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


async def get_user_spendings(table: str, request: Request):
    """
    Get user spendings from the database for specified date range.

    :param table: (str) - table name.
    :param request: (fastapi.Request) - request.
    :return: (JSONResponse) - response with the returned record.
    """
    # Get request parameters.
    request_params = request.query_params

    try:
        is_valid_token, msg, auth_card_id = await validate_token(request_params, request)
    except Exception as err:
        logger.error(f'Validate token error: {err}')
        return JSONResponse(content={'content': 'unauthorized'},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)

    # Check authorization of the request.
    if not is_valid_token:
        return JSONResponse(content={'content': msg}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    if str(auth_card_id) != request_params["card_id"]:
        return JSONResponse(content={'content': 'user can view only data related to him, not ot other users'},
                            status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    try:
        card_id, from_date, to_date = request_params["card_id"], request_params["from_date"], request_params["to_date"]
    except (ValueError, KeyError):
        return JSONResponse(
            content={"content": "Invalid request parameters."}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors
        )

    # Get user spendings.
    spendings = operator.get_user_spendings(table=table, card_id=card_id, from_date=from_date, to_date=to_date)
    print('spendings -- ', spendings)

    # In case there is no such record.
    if not spendings:
        return JSONResponse(
            content={"content": "There is no such record."}, status_code=status.HTTP_200_OK, headers=cors
        )
    return JSONResponse(content={"spendings": spendings}, status_code=status.HTTP_200_OK, headers=cors)


@app.options("/{full_path:path}")
async def options():
    return JSONResponse(status_code=status.HTTP_200_OK, content={"ok": "true"}, headers=cors)


@app.get("/get_spendings_by_days")
async def get_spendings_by_days(request: Request):
    """
    Get user spending for specified in the request day dates.
    Request date has to have the following format: YYYY-MM-DD.

    :param request: (fastapi.Request) - request.
    :return:  (JSONResponse) - response with the returned record.
    """
    return await get_user_spendings(table=TR_PREAGGREGATED_DAILY_TABLE, request=request)


@app.get("/get_spendings_by_months")
async def get_spendings_by_months(request: Request):
    """
    Get user spending for specified in the request day dates.
    Request date has to have the following format: YYYY-MM-DD.

    :param request: (fastapi.Request) - request.
    :return: (JSONResponse) - response with the returned record.
    """
    return await get_user_spendings(table=TR_PREAGGREGATED_MONTHLY_TABLE, request=request)


@app.post("/get_bank_statistics")
async def get_bank_statistics(request: Request):
    """
    Get bank statistics for the specified date.
    Request date has to have the following format: YYYY-MM-DD.

    :param request: (fastapi.Request) - request.
    :return: (JSONResponse) - response with the returned record.
    """
    # Get request parameters.
    request_params = await request.json()
    logger.info(f'request_params: {request_params}')

    try:
        token = request_params["token"]
        date = request_params["date"]
    except (ValueError, KeyError):
        return JSONResponse(
            content={"content": "Invalid request parameters"}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors
        )

    if token != os.getenv("SECRET_TOKEN"):
        return JSONResponse(content={'errors': 'Wrong token'},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)

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


@app.get("/get_bank_statistics_report")
async def get_bank_statistics_report(request: Request):
    # Get request parameters.
    request_params = request.query_params
    logger.info(f'request_params: {request_params}')

    try:
        is_valid_token, msg, auth_card_id = await validate_token(request_params,
                                                                 request=None, token=request_params.get('token'))
    except Exception as err:
        logger.error(f'Validate token error: {err}')
        return JSONResponse(content={'content': 'unauthorized'},
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            headers=cors)

    # Check authorization of the request.
    if not is_valid_token:
        return JSONResponse(content={'content': msg}, status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    # check admin rights
    if str(auth_card_id) != ADMIN_CARD_ID:
        return JSONResponse(content={'content': 'Only admins have access to this endpoint'},
                            status_code=status.HTTP_401_UNAUTHORIZED, headers=cors)

    # If all checks are passed, generate a report and return it
    result = create_bank_stats_report(operator)
    if result == -1:
        return JSONResponse(
            content={"content": "There is no such record."}, status_code=status.HTTP_200_OK, headers=cors
        )

    with open('./report.html', 'r') as html_file:
        content = html_file.read()

    return HTMLResponse(content=content, status_code=200)


@app.on_event("shutdown")
def shutdown():
    print("Closing connection to AnalyticsServiceOperator database...")
    operator.shutdown()
