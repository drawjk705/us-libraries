# pyright: reportUnknownMemberType=false

import pandas as pd
import punq

from us_libraries._client import LibrariesClient
from us_libraries._config import DEFAULT_DATA_DIR, Config
from us_libraries._download.download_service import DownloadService
from us_libraries._download.interface import IDownloadService
from us_libraries._logger.configure_logger import DEFAULT_LOG_FILE, configure_logger
from us_libraries._logger.factory import LoggerFactory
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._scraper.interface import IScrapingService
from us_libraries._scraper.scraping_service import ScrapingService
from us_libraries._stats.interface import IStatsService
from us_libraries._stats.stats_service import StatsService


class Libraries:
    _client: LibrariesClient
    _config: Config

    def __init__(
        self,
        year: int,
        data_dir: str = DEFAULT_DATA_DIR,
        log_file: str = DEFAULT_LOG_FILE,
        should_overwrite_cached_urls: bool = False,
        should_overwrite_existing_cache: bool = False,
    ) -> None:
        config = Config(
            year=year,
            data_dir=data_dir,
            log_file=log_file,
            should_overwrite_cached_urls=should_overwrite_cached_urls,
            should_overwrite_existing_cache=should_overwrite_existing_cache,
        )

        self._config = config

        container = punq.Container()

        # singletons
        container.register(Config, instance=config)

        # services
        container.register(ILoggerFactory, LoggerFactory)
        container.register(IScrapingService, ScrapingService)
        container.register(IDownloadService, DownloadService)
        container.register(IStatsService, StatsService)
        container.register(LibrariesClient)

        configure_logger(log_file, year)

        self._client = container.resolve(LibrariesClient)

    def get_state_summary_data(self) -> pd.DataFrame:
        return self._client.get_state_summary_data()

    def get_system_data(self) -> pd.DataFrame:
        return self._client.get_system_data()

    def get_outlet_data(self) -> pd.DataFrame:
        return self._client.get_outlet_data()

    def __repr__(self) -> str:
        return f"<Libraries {self._config.year}>"

    def __str__(self) -> str:
        return self.__repr__()
