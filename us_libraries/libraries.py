# pyright: reportUnknownMemberType=false

import pandas as pd
import punq

from us_libraries._cache.interface import IOnDiskCache
from us_libraries._cache.on_disk_cache import OnDiskCache
from us_libraries._client import LibrariesClient
from us_libraries._config import DEFAULT_CACHE_DIR, DEFAULT_DATA_DIR, Config
from us_libraries._download.download_service import DownloadService
from us_libraries._download.interface import IDownloadService
from us_libraries._logger.configure_logger import DEFAULT_LOG_FILE, configure_logger
from us_libraries._logger.factory import LoggerFactory
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._scraper.interface import IScrapingService
from us_libraries._scraper.scraping_service import ScrapingService
from us_libraries._stats.interface import IStatsService
from us_libraries._stats.stats_service import StatsService
from us_libraries._variables.extraction_service import VariableExtractionService
from us_libraries._variables.interface import (
    IVariableExtractionService,
    IVariableRepository,
)
from us_libraries._variables.models import DataFileType, VariableSet
from us_libraries._variables.repository import VariableRepository


class Libraries:
    _client: LibrariesClient
    _config: Config

    def __init__(
        self,
        year: int,
        cache_dir: str = DEFAULT_CACHE_DIR,
        data_dir: str = DEFAULT_DATA_DIR,
        log_file: str = DEFAULT_LOG_FILE,
        should_cache_on_disk: bool = False,
        should_overwrite_cached_urls: bool = False,
        should_overwrite_existing_cache: bool = False,
        should_rename_columns: bool = True,
    ) -> None:
        config = Config(
            year=year,
            cache_dir=cache_dir,
            data_dir=data_dir,
            log_file=log_file,
            should_cache_on_disk=should_cache_on_disk,
            should_overwrite_cached_urls=should_overwrite_cached_urls,
            should_overwrite_existing_cache=should_overwrite_existing_cache,
            should_rename_columns=should_rename_columns,
        )

        self._config = config

        container = punq.Container()

        # singletons
        container.register(Config, instance=config)

        # services
        container.register(ILoggerFactory, LoggerFactory)
        container.register(IScrapingService, ScrapingService)
        container.register(IOnDiskCache, OnDiskCache)
        container.register(IDownloadService, DownloadService)
        container.register(IStatsService, StatsService)
        container.register(IVariableExtractionService, VariableExtractionService)
        container.register(IVariableRepository, VariableRepository)
        container.register(LibrariesClient)

        configure_logger(log_file, year)

        self._client = container.resolve(LibrariesClient)

    def get_stats(self, data_file_type: DataFileType, *variables: str) -> pd.DataFrame:
        return self._client.get_stats(data_file_type, *variables)

    @property
    def outlet_data_vars(self) -> VariableSet:
        return self._client.outlet_data_vars

    @property
    def state_summary_vars(self) -> VariableSet:
        return self._client.state_summary_vars

    @property
    def system_data_vars(self) -> VariableSet:
        return self._client.system_data_vars

    def __repr__(self) -> str:
        return f"<Libraries {self._config.year}>"

    def __str__(self) -> str:
        return self.__repr__()
