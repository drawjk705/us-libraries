import logging

import pandas as pd

from us_pls._download.interface import IDownloadService
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._stats.interface import IStatsService


class LibrariesClient:
    _stats_service: IStatsService
    _downloader: IDownloadService
    _logger: logging.Logger

    def __init__(
        self,
        stats_service: IStatsService,
        downloader: IDownloadService,
        logger_factory: ILoggerFactory,
    ) -> None:
        self._stats_service = stats_service
        self._downloader = downloader
        self._logger = logger_factory.get_logger(__name__)

        self.__init_client()

    def get_stats(self, _from: DatafileType) -> pd.DataFrame:
        return self._stats_service.get_stats(_from)

    def read_docs(self, on: DatafileType) -> None:
        self._stats_service.read_docs(on)

    def __init_client(self) -> None:
        # download the resources needed to
        # get things started
        self._logger.info("Initializing client. This may take some time...")

        self._downloader.download()
