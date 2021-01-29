import json
import logging
import os
import shutil
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

import pandas as pd

from us_pls._config import Config
from us_pls._logger.interface import ILoggerFactory
from us_pls._persistence.interface import IOnDiskCache


class OnDiskCache(IOnDiskCache):
    _config: Config
    _logger: logging.Logger

    _cache_path: Path

    def __init__(self, config: Config, logger_factory: ILoggerFactory) -> None:
        self._config = config
        self._logger = logger_factory.get_logger(__name__)

        self._init_cache()

    def exists(self, resource_path: str) -> bool:
        path = self._get_full_path(Path(resource_path))

        return path.exists()

    def put(self, resource: Union[bytes, Dict[str, Any]], resource_path: str) -> None:
        path = self._get_full_path(Path(resource_path))

        self._logger.debug(f"Caching resource in {path}")

        if isinstance(resource, bytes):
            self._put_bytes(resource, path)
        else:
            self._put_json(resource, path)

    def get(  # type: ignore
        self,
        resource_path: str,
        resource_type: Union[Literal["df"], Literal["json"], Literal["txt"]],
    ) -> Optional[Union[Dict[str, Any], pd.DataFrame, str]]:
        path = self._get_full_path(Path(resource_path))

        if not path.exists():
            self._logger.debug(f"Cache miss for {path}")
            return None

        self._logger.debug(f"Cache hit for {path}")

        if resource_type == "json":
            return self._get_json(path)
        if resource_type == "txt":
            return self._get_txt(path)
        if resource_type == "df":
            return pd.read_csv(path)  # type: ignore

    def remove(self, resource_path: Union[Path, PathLike[str]]) -> None:
        path = self._get_full_path(Path(resource_path))

        self._logger.debug(f"Removing {path}")

        if path.is_dir():
            shutil.rmtree(path)
        else:
            os.remove(path)

    def rename(
        self, _from: Union[Path, PathLike[str]], to: Union[Path, PathLike[str]]
    ) -> None:
        from_path = self._get_full_path(_from)
        to_path = self._get_full_path(to)

        self._logger.debug(f"Renaming {from_path} to {to_path}")
        os.rename(from_path, to_path)

    def _get_full_path(self, path: Union[Path, PathLike[str]]) -> Path:
        if self._cache_path in Path(path).parents:
            return Path(path)

        return self._cache_path / Path(path)

    # `put` helpers

    def _put_json(self, resource: Dict[str, Any], resource_path: Path) -> None:
        with open(resource_path, "w") as f:
            json.dump(resource, f)

    def _put_bytes(self, resource: bytes, resource_path: Path) -> None:
        with open(resource_path, "wb") as f:
            f.write(resource)

    # `get` helpers

    def _get_json(self, resource_path: Path) -> Dict[str, Any]:
        with open(resource_path, "r") as f:
            return json.load(f)

    def _get_txt(self, resource_path: Path) -> str:
        with open(resource_path, "r") as f:
            return f.read()

    def _init_cache(self):
        self._logger.debug("Setting up cache")

        self._cache_path = Path(f"{self._config.data_dir}/{self._config.year}")

        if self._cache_path.exists() and self._config.should_overwrite_existing_cache:
            self._logger.debug("Purging cache")

            shutil.rmtree(self._cache_path)

        self._cache_path.mkdir(parents=True, exist_ok=True)
