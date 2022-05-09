from domain_logic.utils.__logger import ServiceLogger
from domain_logic.__constants import *
import logging
import datetime
import os


def get_logger(name) -> logging.Logger:
    """
    Return INFO logger that is writing logs to a file.
    :return: (logging.Logger) - info logger.
    """
    # Create a directory to preserve logs.
    os.makedirs(LOGS_PATH, exist_ok=True)
    os.makedirs(f"{LOGS_PATH}{name}", exist_ok=True)

    filepath = f"{LOGS_PATH}{name}/logs_{datetime.datetime.utcnow().timestamp()}.log"

    # Introduce a bare logger.
    logging.basicConfig(level=logging.INFO)
    # Create Info Logger.
    ilogger = logging.getLogger(name)
    info_logger = ServiceLogger(name, filepath)
    ilogger.addHandler(info_logger)
    return ilogger
