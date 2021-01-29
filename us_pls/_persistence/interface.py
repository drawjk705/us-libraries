from abc import ABC
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union, overload

import pandas as pd


class IOnDiskCache(ABC):
    _cache_path: Path

    def exists(self, resource_path: str) -> bool:
        ...

    def put(self, resource: Union[bytes, Dict[str, Any]], resource_path: str) -> None:
        ...

    @overload
    def get(self, resource_path: str, resource_type: Literal["txt"]) -> Optional[str]:
        ...

    @overload
    def get(
        self, resource_path: str, resource_type: Literal["json"]
    ) -> Optional[Dict[str, Any]]:
        ...

    @overload
    def get(
        self, resource_path: str, resource_type: Literal["df"]
    ) -> Optional[pd.DataFrame]:
        ...

    def get(self, resource_path, resource_type):  # type: ignore
        ...

    def remove(self, resource_path: Union[Path, PathLike[str]]) -> None:
        ...

    def rename(
        self, _from: Union[Path, PathLike[str]], to: Union[Path, PathLike[str]]
    ) -> None:
        ...

    @property
    def cache_path(self) -> Path:
        return self._cache_path
