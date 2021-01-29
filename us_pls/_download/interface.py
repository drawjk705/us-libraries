from abc import ABC, abstractmethod


class IDownloadService(ABC):
    @abstractmethod
    def download(self) -> None:
        ...
