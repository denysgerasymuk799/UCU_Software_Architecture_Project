import logging


class ServiceLogger(logging.FileHandler):
    def __init__(self, logger_name, filename):
        self.logger_name = logger_name
        logging.FileHandler.__init__(self, filename)
        self.setLevel(logging.INFO)
        self.__set_format()

    def __set_format(self):
        fmt = '\U00002705 [%(levelname)s] - [%(asctime)s] - (%(filename)s).%(funcName)s(%(lineno)d): %(message)s'
        fmt_date = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(fmt, fmt_date)
        self.setFormatter(formatter)

    def __str__(self):
        return self.logger_name
