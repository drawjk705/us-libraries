# pyright: reportUnknownMemberType=false

import logging
import re
from typing import Dict, List

import pandas as pd

from us_pls._config import Config
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._persistence.interface import IOnDiskCache
from us_pls._stats.interface import IStatsService


class StatsService(IStatsService):
    _config: Config
    _cache: IOnDiskCache
    _logger: logging.Logger

    _documentation: Dict[DatafileType, str]

    def __init__(
        self, config: Config, cache: IOnDiskCache, logger_factory: ILoggerFactory
    ) -> None:
        self._config = config
        self._cache = cache
        self._logger = logger_factory.get_logger(__name__)

        self._documentation = {}

    def get_stats(self, _from: DatafileType) -> pd.DataFrame:
        self._logger.debug(f"Getting stats for {_from.value}")

        stats = self._cache.get(_from.value, "df")

        if stats is None:
            return pd.DataFrame()

        return stats

    def read_docs(self, on: DatafileType) -> None:
        self._logger.debug(f"Reading docs on {on.value}")

        self._get_documentation()

        documentation = self._documentation.get(on)

        if documentation is None:
            print("No readme exists for this year")
            return

        print(documentation)

    def _get_documentation(self) -> None:
        if len(self._documentation) > 0:
            self._logger.debug("Already pulled documentation")
            return

        readme = self._cache.get("README.txt", "txt")

        if readme is None:
            self._logger.debug("No readme exists")
            return

        documentation: List[str] = []

        in_relevant_documentation = False

        current_doc_string = ""

        consecutive_newline_count = 0

        self._logger.debug("Pulling documentation...")

        for line in readme.splitlines(keepends=True):
            if line == "\n":
                consecutive_newline_count += 1
            else:
                consecutive_newline_count = 0

            stripped_line = " ".join(line.strip().split())

            # for the main bullet point
            if re.match(r"^\d\.", stripped_line) or consecutive_newline_count >= 2:
                if len(current_doc_string) > 0:
                    if re.match(r"^\d\.", current_doc_string):
                        new_doc_string = re.sub(
                            r"^\d\. ", "", current_doc_string.strip(" ").strip("\n")
                        )

                        documentation.append(new_doc_string)

                in_relevant_documentation = True
                current_doc_string = stripped_line
                continue

            if re.match(r"^[a-z]\.", stripped_line):
                current_doc_string += "\n    " + stripped_line
                continue

            if not in_relevant_documentation:
                continue

            current_doc_string += " " + stripped_line

        for doc in documentation:
            if (
                "System Data File" in doc[:200]
                and self._documentation.get(DatafileType.SystemData) is None
            ):
                self._documentation[DatafileType.SystemData] = doc
            elif "State Summary/State Characteristics Data File" in doc[:200]:
                self._documentation[
                    DatafileType.StateSummaryAndCharacteristicData
                ] = doc
            elif "Outlet Data File" in doc[:200]:
                self._documentation[DatafileType.OutletData] = doc

        self._logger.debug("Pulled documentation")
