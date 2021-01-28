from abc import ABC, abstractmethod

import pandas as pd


class IStatsService(ABC):
    @abstractmethod
    def get_system_data(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_state_summary_data(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_outlet_data(self) -> pd.DataFrame:
        ...
