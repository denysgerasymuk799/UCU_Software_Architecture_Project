import logging
from flask import Flask

from domain_logic.custom_logger import MyHandler

# create main app
app = Flask(__name__)

# config for security in forms and other things
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

logger = logging.getLogger('root')
logger.setLevel('INFO')
logging.disable(logging.DEBUG)
logger.addHandler(MyHandler())
