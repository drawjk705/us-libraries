from abc import ABC, abstractmethod

import pandas as pd

from us_libraries._variables.models import DataFileType


class IStatsService(ABC):
    @abstractmethod
    def get_stats(self, data_file_type: DataFileType, *variables: str) -> pd.DataFrame:
        ...
