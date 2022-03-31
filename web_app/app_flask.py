import json
import requests as req
from flask import Flask, redirect, url_for, render_template, request, session, jsonify

from init_config import app, logger


@app.route('/', methods=['GET'])
def home_page():
    return redirect(url_for('login'))


@app.route('/registration', methods=['GET', 'POST'])
def registration_get():
    if request.method == 'GET':
        return render_template("registration.html")

    # TODO: add validations from the Frontend side
    print('request.form.to_dict() -- ', request.form.to_dict())
    response = req.post(url='http://localhost:8000/registration',
                        headers={"Accept": "application/json"},
                        data=request.form.to_dict())
    print('response -- ', response.json())

    if 200 <= response.status_code <= 300:
        return redirect(url_for('login'))

    data = {
        'errors': f'New user id is {response.json().get("errors")}'
    }
    response = app.response_class(
        response=json.dumps(data),
        status=response.status_code,
        mimetype='application/json'
    )
    return response


@app.route('/login', methods=['GET'])
def login():
    return render_template("login.html")


@app.route('/login', methods=['GET'])
def profile_page():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=8001, debug=True)
