import logging

import pandas as pd

from us_libraries._download.interface import IDownloadService
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._stats.interface import IStatsService
from us_libraries._variables.interface import IVariableRepository
from us_libraries._variables.models import DataFileType, VariableSet


class LibrariesClient:
    _stats_service: IStatsService
    _variable_repo: IVariableRepository
    _downloader: IDownloadService
    _logger: logging.Logger

    def __init__(
        self,
        stats_service: IStatsService,
        variable_repo: IVariableRepository,
        downloader: IDownloadService,
        logger_factory: ILoggerFactory,
    ) -> None:
        self._stats_service = stats_service
        self._variable_repo = variable_repo
        self._downloader = downloader
        self._logger = logger_factory.get_logger(__name__)

        self.__init_client()

    def get_stats(self, data_file_type: DataFileType, *variables: str) -> pd.DataFrame:
        return self._stats_service.get_stats(data_file_type, *variables)

    @property
    def outlet_data_vars(self) -> VariableSet:
        return self._variable_repo.outlet_data

    @property
    def state_summary_vars(self) -> VariableSet:
        return self._variable_repo.state_summary

    @property
    def system_data_vars(self) -> VariableSet:
        return self._variable_repo.system_data

    def __init_client(self) -> None:
        # download the resources needed to
        # get things started
        self._logger.info("Scraping Public Libraries Survey page for data...")
        self._downloader.download()
        # populate the variable repo
        self._logger.info(
            "Parsing downloaded variables. If you do not have cached results from a previous session, this may take some time."
        )
        self._variable_repo.get_variables()
