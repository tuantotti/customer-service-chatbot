import logging
import os
from datetime import datetime


class LoggerFactory(object):
    _logger = None

    def __init__(self, log_level: str = "INFO") -> None:
        self.log_level = log_level

    def get_logger(self):
        if self._logger is None:
            self._logger = logging.getLogger()
            log_formater = logging.Formatter(
                "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(log_formater)
            self._logger.addHandler(console_handler)

            # set the logging level based on the user selection
            if self.log_level == "INFO":
                self._logger.setLevel(logging.INFO)
            elif self.log_level == "ERROR":
                self._logger.setLevel(logging.ERROR)
            elif self.log_level == "DEBUG":
                self._logger.setLevel(logging.DEBUG)
            elif self.log_level == "WARNING":
                self._logger.setLevel(logging.WARNING)
            elif self.log_level == "CRITICAL":
                self._logger.setLevel(logging.CRITICAL)
            if not os.path.isdir("./log"):
                os.mkdir("./log", mode=0o777)
            parent_log_dir = f'./log/log_{datetime.now().strftime("%m-%d-%Y")}'
            if not os.path.isdir(parent_log_dir):
                os.mkdir(parent_log_dir, mode=0o777)
            file_handler = logging.FileHandler(os.path.join(parent_log_dir, "logs.log"))
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(log_formater)

            self._logger.addHandler(file_handler)

        return self._logger


Logger = LoggerFactory("INFO")
