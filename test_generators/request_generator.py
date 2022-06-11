import time
import random
import logging
import requests as req

from datetime import datetime

from constants import *
from custom_logger import CustomHandler


# Prepare own helper class objects
logger = logging.getLogger('test_generator')
if DEBUG_MODE:
    logger.setLevel('DEBUG')
else:
    logger.setLevel('INFO')
    logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())


def make_registration_request():
    datetime_now = datetime.now().strftime("%d_%m_%Y__%H_%M_%S_%f")[:-3]
    payload = {
        "firstname": f"test",
        "lastname": f"test",
        "email": f"test_user_{datetime_now}@gmail.com",
        "password": "123456",
        "repeat_password": "123456",
        "birthday_date": "01/01/2000",
        "city": "Lviv",
        "address": f"address_{datetime_now}",
    }
    url = REGISTRATION_ENDPOINT
    try:
        resp = req.post(url, data=payload)
        if resp.status_code != 200:
            logger.error(f'Failed payload: {payload}')
            logger.error(f'Bad response code for {REGISTRATION_REQUEST} request: {resp.json()}')
        else:
            logger.info(f'Successfully send the following {REGISTRATION_REQUEST} request: {payload}')
    except Exception as err:
        logger.error(f'Sending {REGISTRATION_REQUEST} request error: {err}')
        logger.error(f'Failed payload: {payload}')


def make_topup_request():
    amount = random.randint(1, 500)
    card_id = random.choice(USER_CARDS)
    payload = {
        "card_id": card_id,
        "receiver_card_id": card_id,
        "amount": str(amount),
        "transaction_type": "BALANCE_TOP_UP",
        "token": GENERATOR_TOKEN
    }
    url = TOPUP_ENDPOINT
    try:
        resp = req.post(url, data=payload)
        if resp.status_code != 200:
            logger.error(f'Failed payload: {payload}')
            logger.error(f'Bad response code for {TOPUP_REQUEST} request: {resp.json()}')
        else:
            logger.info(f'Successfully send the following {TOPUP_REQUEST} request: {payload}')
    except Exception as err:
        logger.error(f'Sending {TOPUP_REQUEST} request error: {err}')


def make_transaction_request():
    amount = random.randint(1, 500)
    card_id, receiver_card_id = random.sample(USER_CARDS, 2)
    payload = {
        "card_id": card_id,
        "receiver_card_id": receiver_card_id,
        "amount": str(amount),
        "transaction_type": "TRANSFER",
        "token": GENERATOR_TOKEN
    }
    url = TRANSACTION_ENDPOINT
    try:
        resp = req.post(url, data=payload)
        if resp.status_code != 200:
            logger.error(f'Failed payload: {payload}')
            logger.error(f'Bad response code for {TRANSACTION_REQUEST} request: {resp.json()}')
        else:
            logger.info(f'Successfully send the following {TRANSACTION_REQUEST} request: {payload}')
    except Exception as err:
        logger.error(f'Sending {TRANSACTION_REQUEST} request error: {err}')


def run_generator():
    # Define possible options
    request_type_options = [REGISTRATION_REQUEST] + [MONEY_REQUEST for _ in range(100)]  # 1:100 ratio
    money_request_options = [TOPUP_REQUEST, TRANSACTION_REQUEST]  # 1:1 ratio
    option_to_request_function = {
        REGISTRATION_REQUEST: make_registration_request,
        TOPUP_REQUEST: make_topup_request,
        TRANSACTION_REQUEST: make_transaction_request,
    }

    n_requests = 0
    requests_per_second = 10
    total_start_time = datetime.now()
    start_time = time.time()
    while True:
        # Choose random request type
        option = random.choice(request_type_options)
        if option == REGISTRATION_REQUEST:
            option_to_request_function[option]()
        else:
            # Choose random money request
            money_request_option = random.choice(money_request_options)
            option_to_request_function[money_request_option]()

        n_requests += 1
        if n_requests % requests_per_second == 0:
            end_time = time.time()
            time_diff = end_time - start_time

            if time_diff < 1:
                sleep_time = 1 - time_diff
                # Note that sleep in python is quite effective in our case:
                # https://stackoverflow.com/questions/10926328/efficient-and-fast-python-while-loop-while-using-sleep
                time.sleep(sleep_time)

            start_time = time.time()

        # Periodically make execution time logs
        if n_requests % 50 == 0:
            cur_time = datetime.now()
            print('Request number: ', n_requests)
            print('Time from the generator start (in minutes): ', (cur_time - total_start_time).total_seconds() // 60)
            print('Time from the generator start (in hours): ', (cur_time - total_start_time).total_seconds() / 3600)


if __name__ == '__main__':
    run_generator()
