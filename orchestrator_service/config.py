import asyncio
import logging

from domain_logic.utils.custom_logger import CustomHandler
from domain_logic.__constants import *

kafka_loop = asyncio.get_event_loop()

# Prepare own helper class objects
logger = logging.getLogger('root')
if DEBUG_MODE:
    logger.setLevel('DEBUG')
else:
    logger.setLevel('INFO')
    logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())
