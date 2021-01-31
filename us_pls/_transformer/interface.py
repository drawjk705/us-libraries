from abc import ABC, abstractmethod

import pandas as pd

from us_pls._download.models import DatafileType


class ITransformationService(ABC):
    @abstractmethod
    def transform_columns(
        self, df: pd.DataFrame, datafile_type: DatafileType
    ) -> pd.DataFrame:
        ...
