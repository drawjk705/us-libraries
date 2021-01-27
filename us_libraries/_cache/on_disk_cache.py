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

    def get(
        self, resource_path: str, should_get_from_root_cache: bool = False
    ) -> pd.DataFrame:
        full_path = (
            self._cache_path
            if not should_get_from_root_cache
            else self._cache_path.parent
        ) / Path(resource_path)

        if not full_path.exists():
            return pd.DataFrame()

        return pd.read_csv(full_path.name)  # type: ignore

    def put(
        self,
        resource_path: str,
        resource: pd.DataFrame,
        should_store_in_root_cache: bool = False,
    ) -> None:
        full_path = (
            self._cache_path
            if not should_store_in_root_cache
            else self._cache_path.parent
        ) / Path(resource_path)

        resource.to_csv(full_path.name)  # type: ignore

    def _init_cache(self):
        self._cache_path = Path(f"{self._config.cache_dir}/{self._config.year}")
        self._cache_path.mkdir(parents=True, exist_ok=True)
