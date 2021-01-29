import logging

from us_pls._logger.interface import ILoggerFactory


class LoggerFactory(ILoggerFactory):
    def __init__(self) -> None:
        super().__init__()

    def get_logger(self, name: str) -> logging.Logger:
        return logging.getLogger(name)
