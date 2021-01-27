from abc import ABC, abstractmethod
from typing import Dict


class IScrapingService(ABC):
    @abstractmethod
    def scrape_files(self) -> Dict[str, Dict[str, str]]:
        pass
