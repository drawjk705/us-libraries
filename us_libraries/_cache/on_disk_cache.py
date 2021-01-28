import shutil
from pathlib import Path

import pandas as pd

from us_libraries._cache.interface import IOnDiskCache
from us_libraries._config import Config


class OnDiskCache(IOnDiskCache):
    _config: Config
    _cache_path: Path

    def __init__(self, config: Config) -> None:
        self._config = config

        self._init_cache()

    def get(self, resource_path: str) -> pd.DataFrame:
        if not self._config.should_cache_on_disk:
            return pd.DataFrame()

        full_path = (self._cache_path) / Path(resource_path)

        if not full_path.exists():
            return pd.DataFrame()

        return pd.read_csv(full_path)  # type: ignore

    def put(
        self,
        resource_path: str,
        resource: pd.DataFrame,
    ) -> None:
        full_path = (self._cache_path) / Path(resource_path)

        if not self._config.should_cache_on_disk or full_path.exists():
            return

        resource.to_csv(full_path)

    def _init_cache(self):
        self._cache_path = Path(f"{self._config.cache_dir}/{self._config.year}")

        if self._config.should_cache_on_disk:
            self._cache_path.mkdir(parents=True, exist_ok=True)

            if self._config.should_overwrite_existing_cache:
                shutil.rmtree(self._cache_path)

                self._cache_path.mkdir(parents=True, exist_ok=True)
