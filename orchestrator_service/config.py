import asyncio
import logging

from domain_logic.utils.custom_logger import CustomHandler

loop2 = asyncio.get_event_loop()

# Prepare own helper class objects
logger = logging.getLogger('root')
logger.setLevel('DEBUG')
# logger.setLevel('INFO')
# logging.disable(logging.DEBUG)
logger.addHandler(CustomHandler())
