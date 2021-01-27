from abc import ABC

import pandas as pd


class IOnDiskCache(ABC):
    def get(
        self, resource_path: str, should_get_from_root_cache: bool = False
    ) -> pd.DataFrame:
        ...

    def put(
        self,
        resource_path: str,
        resource: pd.DataFrame,
        should_store_in_root_cache: bool = False,
    ) -> None:
        ...
