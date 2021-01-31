import logging

import pandas as pd

from us_pls._download.interface import IDownloadService
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._stats.interface import IStatsService
from us_pls._variables.interface import IVariableRepository
from us_pls._variables.models import Variables


class LibrariesClient:
    _stats_service: IStatsService
    _downloader: IDownloadService
    _variable_repo: IVariableRepository
    _logger: logging.Logger

    def __init__(
        self,
        stats_service: IStatsService,
        downloader: IDownloadService,
        variable_repo: IVariableRepository,
        logger_factory: ILoggerFactory,
    ) -> None:
        self._stats_service = stats_service
        self._downloader = downloader
        self._variable_repo = variable_repo
        self._logger = logger_factory.get_logger(__name__)

        self.__init_client()

    def get_stats(self, _from: DatafileType) -> pd.DataFrame:
        return self._stats_service.get_stats(_from)

    def read_docs(self, on: DatafileType) -> None:
        self._stats_service.read_docs(on)

    @property
    def summary_data_vars(self) -> Variables:
        return self._variable_repo.summary_data_vars

    @property
    def system_data_vars(self) -> Variables:
        return self._variable_repo.system_data_vars

    @property
    def outlet_data_vars(self) -> Variables:
        return self._variable_repo.outlet_data_vars

    def __init_client(self) -> None:
        # download the resources needed to
        # get things started
        self._logger.info("Initializing client. This may take some time...")

        self._downloader.download()
