import json
import requests as req
from flask import redirect, url_for

from init_config import app, logger
from constants import *


def auth_service_request(request_type: str, is_valid: bool, endpoint: str, request_data: dict,
                         redirect_endpoint: str,
                         make_authorization: bool, access_token: str = None, possible_error_code: int = 400):
    response = req.Response()
    response._content = {'errors': 'Invalid input'}
    response.status_code = possible_error_code
    if is_valid:
        logger.info(f'{request_type} request on {endpoint}, data -- {request_data}')
        headers = {"Accept": "application/json"}
        if make_authorization:
            headers["Authorization"] = access_token

        if request_type == 'GET':
            response = req.get(url=f'{API_base_link}/{endpoint}',
                               headers=headers,
                               params=request_data)
        else:
            response = req.post(url=f'{API_base_link}/{endpoint}',
                                headers=headers,
                                data=request_data)
        logger.info(f'Response on the request -- {response.json()}')

        if 200 <= response.status_code < 400:
            return redirect(url_for(redirect_endpoint))

    data = {
        'errors': '\n'.join(response.json().get("errors"))
    }
    response = app.response_class(
        response=json.dumps(data),
        status=response.status_code,
        mimetype='application/json'
    )
    return response
