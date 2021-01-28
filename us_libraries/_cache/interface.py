from abc import ABC

import pandas as pd


class IOnDiskCache(ABC):
    def get(
        self,
        resource_path: str,
    ) -> pd.DataFrame:
        ...

    def put(
        self,
        resource_path: str,
        resource: pd.DataFrame,
    ) -> None:
        ...
