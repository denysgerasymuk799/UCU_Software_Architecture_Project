import configparser
from flask import Flask, render_template, request, redirect, url_for

from src.producer import TransactionProducer


app = Flask(__name__)
transaction_producer = TransactionProducer()

config = configparser.ConfigParser()
config.read("config.ini")

# Setting configuration values
MONEY_TRANSACTION_TOPIC = config['Producer']['money_transaction_topic']
ip_address = config['Producer']['ip_address']


@app.route('/')
def init():
    return redirect(url_for('form'))


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/data/', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form

        messages = []
        for i in range(10):
            msg = {
                'transaction_id': 123,
                'from_card_number': 8888888888888888,
                'to_card_number': 7777777777777777,
                'amount': 1000_000,
                'currency': 'UAH',
                'comment': 'For support of the Armed Forces of Ukraine'
            }
            messages.append(msg)

        transaction_producer.send_messages(MONEY_TRANSACTION_TOPIC, messages)
        return render_template('data.html', form_data=form_data)


if __name__ == '__main__':
    app.run(host='localhost', port=5000)
