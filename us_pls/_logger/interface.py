import logging
from abc import ABC, abstractmethod


class ILoggerFactory(ABC):
    @abstractmethod
    def get_logger(self, name: str) -> logging.Logger:
        ...
