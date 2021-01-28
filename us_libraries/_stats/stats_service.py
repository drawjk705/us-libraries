# pyright: reportUnknownMemberType=false

import pandas as pd

from us_libraries._config import Config
from us_libraries._download.models import DatafileType
from us_libraries._stats.interface import IStatsService


class StatsService(IStatsService):
    _config: Config

    def __init__(self, config: Config) -> None:
        self._config = config

    def get_system_data(self) -> pd.DataFrame:
        return self._get_stats(DatafileType.SystemData)

    def get_state_summary_data(self) -> pd.DataFrame:
        return self._get_stats(DatafileType.StateSummaryAndCharacteristicData)

    def get_outlet_data(self) -> pd.DataFrame:
        return self._get_stats(DatafileType.OutletData)

    def _get_stats(self, datafile_type: DatafileType) -> pd.DataFrame:
        stats: pd.DataFrame = pd.read_csv(
            f"{self._config.data_dir}/{self._config.year}/{datafile_type.value}"
        )

        return stats
