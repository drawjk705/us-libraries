import pandas as pd

from us_libraries._stats.interface import IStatsService
from us_libraries._variables.interface import IVariableRepository
from us_libraries._variables.models import DataFileType, VariableSet


class LibrariesClient:
    _stats_service: IStatsService
    _variable_repo: IVariableRepository

    def __init__(
        self, stats_service: IStatsService, variable_repo: IVariableRepository
    ) -> None:
        self._stats_service = stats_service
        self._variable_repo = variable_repo

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
