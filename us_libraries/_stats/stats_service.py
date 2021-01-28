from typing import Dict

import pandas as pd

from us_libraries._config import Config
from us_libraries._download.models import DownloadType
from us_libraries._stats.interface import IStatsService
from us_libraries._variables.interface import IVariableRepository
from us_libraries._variables.models import DataFileType

data_file_type_to_download_type: Dict[DataFileType, DownloadType] = {
    DataFileType.OutletData: DownloadType.OutletData,
    DataFileType.StateSummary: DownloadType.StateSummaryAndCharacteristicData,
    DataFileType.SystemData: DownloadType.SystemData,
}


class StatsService(IStatsService):
    _config: Config
    _variable_repo: IVariableRepository

    def __init__(self, config: Config, variable_repo: IVariableRepository) -> None:
        self._config = config
        self._variable_repo = variable_repo

    def get_stats(self, data_file_type: DataFileType, *variables: str) -> pd.DataFrame:
        df = self._variable_repo.get_variables(data_file_type)

        if df is None:
            return pd.DataFrame()

        vars_dict = df.to_dict("records")

        stats: pd.DataFrame = pd.read_csv(  # type: ignore
            f"{self._config.data_dir}/{data_file_type_to_download_type[data_file_type].value}"
        )

        column_mapping: Dict[str, str] = (
            {record["short_name"]: record["long_name"] for record in vars_dict}
            if self._config.should_rename_columns
            else {}
        )

        renamed_stats = stats.rename(columns=column_mapping)

        if len(variables) > 0:
            return renamed_stats[list(variables)]
        return renamed_stats
