# pyright: reportUnknownMemberType=false

import re
from typing import Dict, List

import pandas as pd

from us_libraries._config import Config
from us_libraries._download.models import DatafileType
from us_libraries._stats.interface import IStatsService


class StatsService(IStatsService):
    _config: Config

    _documentation: Dict[DatafileType, str]

    def __init__(self, config: Config) -> None:
        self._config = config

        self._documentation = {}

    def get_stats(self, from_: DatafileType) -> pd.DataFrame:
        stats: pd.DataFrame = pd.read_csv(
            f"{self._config.data_dir}/{self._config.year}/{from_.value}"
        )

        return stats

    def read_docs(self, on: DatafileType) -> None:
        self._get_documentation()

        documentation = self._documentation.get(on)

        print(documentation)

    def _get_documentation(self) -> None:
        if len(self._documentation) > 0:
            return

        with open(f"{self._config.data_dir}/{self._config.year}/README.txt", "r") as f:
            readme_text = f.read()

        documentation: List[str] = []

        in_relevant_documentation = False

        current_doc_string = ""

        consecutive_newline_count = 0

        for line in readme_text.splitlines(keepends=True):
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
