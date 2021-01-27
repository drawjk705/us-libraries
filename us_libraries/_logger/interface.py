from abc import ABC, abstractmethod
import logging


class ILoggerFactory(ABC):
    @abstractmethod
    def get_logger(self, name: str) -> logging.Logger:
        ...