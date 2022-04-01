import json
import requests as req
from flask import redirect, url_for, make_response

from init_config import app, logger
from domain_logic.constants import *


def auth_service_request(request_type: str, is_valid: bool, api_link: str, endpoint: str, request_data: dict,
                         make_authorization: bool, access_token: str = None, possible_error_code: int = 400):
    response = req.Response()
    response._content = {'errors': 'Invalid input'}
    response.status_code = possible_error_code
    if is_valid:
        headers = {"Accept": "application/json"}
        if make_authorization:
            headers["Authorization"] = access_token

        logger.info(f'{request_type} request on {endpoint}, data -- {request_data}')
        if request_type == 'GET':
            response = req.get(url=f'{api_link}/{endpoint}',
                               headers=headers,
                               params=request_data)
        else:
            response = req.post(url=f'{api_link}/{endpoint}',
                                headers=headers,
                                data=request_data)
        logger.info(f'Response on the request -- {response.json()}')

    return response


def return_response(is_valid, response, redirect_endpoint: str = None, cookie: list = None):
    if is_valid and 200 <= response.status_code < 400:
        if redirect_endpoint:
            response = make_response(redirect(url_for(redirect_endpoint)))
        else:
            response = app.response_class(
                response=json.dumps(response.json()),
                status=response.status_code,
                mimetype='application/json'
            )
        if cookie:
            response.set_cookie(cookie[0]['key'], cookie[0]['value'])
        return response

    logger.info(f'response.json().get("errors") -- {response.json().get("errors")}')
    data = {
        'errors': '\n'.join(response.json().get("errors"))
    }
    response = app.response_class(
        response=json.dumps(data),
        status=response.status_code,
        mimetype='application/json'
    )
    return response
