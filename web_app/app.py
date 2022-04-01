from flask import redirect, url_for, render_template, request
from copy import copy

from init_config import app
from domain_logic.forms import LoginForm, TransactionForm
from domain_logic.utils import auth_service_request, return_response


@app.route('/', methods=['GET'])
def home_page():
    return redirect(url_for('login'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template("registration.html")

    # TODO: add validations from the Frontend side
    response = auth_service_request(request_type='POST', is_valid=True, endpoint='registration',
                                    request_data=request.form.to_dict(),
                                    make_authorization=False)
    return return_response(is_valid=True, response=response, redirect_endpoint='login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    # TODO: add validations from the Frontend side
    form = LoginForm(request)
    form.load_data()
    response = auth_service_request(request_type='POST', is_valid=form.is_valid(), endpoint='login',
                                    request_data=request.form.to_dict(),
                                    make_authorization=False, possible_error_code=402)
    if 'access_token' in response.json().keys():
        return return_response(is_valid=form.is_valid(), response=response, redirect_endpoint='profile_page',
                               cookie=[{
                                   'key': 'access_token',
                                   'value': f"Bearer {response.json().get('access_token')}"
                               }])
    return return_response(is_valid=form.is_valid(), response=response, redirect_endpoint='profile_page')


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
    request_data = copy(form.__dict__)
    request_data.pop('request', None)
    request_data.pop('errors', None)
    response = auth_service_request(request_type='POST', is_valid=form.is_valid(),
                                    endpoint='transactions/handle_transaction',
                                    request_data=request_data,
                                    access_token=request.cookies.get('access_token'),
                                    make_authorization=True, possible_error_code=402)
    return return_response(is_valid=form.is_valid(), response=response)


if __name__ == '__main__':
    app.run(port=8001, debug=True)
