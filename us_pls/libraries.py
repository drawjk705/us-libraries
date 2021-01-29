# pyright: reportUnknownMemberType=false

import pandas as pd
import punq

from us_pls._client import LibrariesClient
from us_pls._config import DEFAULT_DATA_DIR, Config
from us_pls._download.download_service import DownloadService
from us_pls._download.interface import IDownloadService
from us_pls._download.models import DatafileType
from us_pls._logger.configure_logger import DEFAULT_LOG_FILE, configure_logger
from us_pls._logger.factory import LoggerFactory
from us_pls._logger.interface import ILoggerFactory
from us_pls._persistence.interface import IOnDiskCache
from us_pls._persistence.on_disk_cache import OnDiskCache
from us_pls._scraper.interface import IScrapingService
from us_pls._scraper.scraping_service import ScrapingService
from us_pls._stats.interface import IStatsService
from us_pls._stats.stats_service import StatsService


class PublicLibrariesSurvey:
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
        container.register(IOnDiskCache, OnDiskCache)
        container.register(LibrariesClient)

        configure_logger(log_file, year)

        self._client = container.resolve(LibrariesClient)

    def get_stats(self, _from: DatafileType) -> pd.DataFrame:
        return self._client.get_stats(_from)

    def read_docs(self, on: DatafileType) -> None:
        return self._client.read_docs(on)

    def __repr__(self) -> str:
        return f"<PublicLibrariesSurvey {self._config.year}>"

    def __str__(self) -> str:
        return self.__repr__()
