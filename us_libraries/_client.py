import logging

import pandas as pd

from us_libraries._download.interface import IDownloadService
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._stats.interface import IStatsService


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

    def get_state_summary_data(self) -> pd.DataFrame:
        return self._stats_service.get_state_summary_data()

    def get_system_data(self) -> pd.DataFrame:
        return self._stats_service.get_system_data()

    def get_outlet_data(self) -> pd.DataFrame:
        return self._stats_service.get_outlet_data()

    def __init_client(self) -> None:
        # download the resources needed to
        # get things started
        self._logger.info("Scraping Public Libraries Survey page for data...")
        self._downloader.download()
