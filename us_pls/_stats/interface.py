from abc import ABC, abstractmethod

import pandas as pd

from us_pls._download.models import DatafileType


class IStatsService(ABC):
    @abstractmethod
    def get_stats(self, _from: DatafileType) -> pd.DataFrame:
        ...

    @abstractmethod
    def read_docs(self, on: DatafileType) -> None:
        ...
