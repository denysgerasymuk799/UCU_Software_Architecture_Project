import json
import requests as req
from flask import redirect, url_for, render_template, request

from init_config import app
from auth.forms import LoginForm, TransactionForm
from utils_flask import auth_service_request


@app.route('/', methods=['GET'])
def home_page():
    return redirect(url_for('login'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template("registration.html")

    # TODO: add validations from the Frontend side
    print('request.form.to_dict() -- ', request.form.to_dict())
    return auth_service_request(request_type='POST', is_valid=True, endpoint='registration',
                                request_data=request.form.to_dict(), redirect_endpoint='login',
                                make_authorization=False)

    # response = req.post(url='http://localhost:8000/registration',
    #                     headers={"Accept": "application/json"},
    #                     data=request.form.to_dict())
    # print('response -- ', response.json())
    #
    # if 200 <= response.status_code <= 300:
    #     return redirect(url_for('login'))
    #
    # data = {
    #     'errors': '\n'.join(response.json().get("errors"))
    # }
    # response = app.response_class(
    #     response=json.dumps(data),
    #     status=response.status_code,
    #     mimetype='application/json'
    # )
    # return response


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    form = LoginForm(request)
    form.load_data()
    if form.is_valid():
        # TODO: add validations from the Frontend side
        print('request.form.to_dict() -- ', request.form.to_dict())
        response = req.post(url='http://localhost:8000/login',
                            headers={"Accept": "application/json"},
                            data=request.form.to_dict())
        print('response -- ', response.json())

        if 200 <= response.status_code < 400:
            return redirect(url_for('profile_page'))

    data = {
        'errors': '\n'.join(response.json().get("errors"))
    }
    response = app.response_class(
        response=json.dumps(data),
        status=402,
        mimetype='application/json'
    )
    return response


@app.route('/profile_page', methods=['GET'])
def profile_page():
    return render_template("index.html")


@app.route('/transactions/handle_transaction', methods=['POST'])
def handle_transaction():
    form = TransactionForm(request)
    form.card_from = "4444444444444444"
    form.card_from_cvv = "123"
    form.card_from_exp_date_month = "12"
    form.card_from_exp_date_year = "24"
    form.card_to = "5555555555555555"

    form.load_data()
    if form.is_valid():
        # TODO: add validations from the Frontend side
        print('request.form.to_dict() -- ', request.form.to_dict())
        response = req.post(url='http://localhost:8000/transactions/handle_transaction',
                            headers={"Accept": "application/json"},
                            data=request.form.to_dict())
        print('response -- ', response.json())

        if 200 <= response.status_code < 400:
            return redirect(url_for('profile_page'))

    data = {
        'errors': '\n'.join(form.__dict__.get("errors"))
    }
    response = app.response_class(
        response=json.dumps(data),
        status=402,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run(port=8001, debug=True)
