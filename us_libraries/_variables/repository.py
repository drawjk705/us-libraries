# pyright: reportUnknownMemberType=false


import logging
from typing import Dict, List, Optional, cast

import pandas as pd

from us_libraries._logger.interface import ILoggerFactory
from us_libraries._variables.interface import (
    IVariableExtractionService,
    IVariableRepository,
)
from us_libraries._variables.models import DataFileType, VariableSet


class VariableRepository(IVariableRepository):
    _system_data: VariableSet
    _state_summary: VariableSet
    _outlet_data: VariableSet

    _extractor: IVariableExtractionService
    _logger: logging.Logger

    def __init__(
        self,
        extractor: IVariableExtractionService,
        logger_factory: ILoggerFactory,
    ) -> None:
        self._extractor = extractor
        self._logger = logger_factory.get_logger(__name__)

        self._system_data = VariableSet()
        self._state_summary = VariableSet()
        self._outlet_data = VariableSet()

    def get_variables(
        self, data_file_type: Optional[DataFileType] = None
    ) -> Optional[pd.DataFrame]:
        dfs = self._extractor.extract_variables_from_documentation_pdf()

        if dfs is None:
            self._logger.info("could not extract any variables from documentation PDF")
            return None

        for file_type, df in dfs.items():
            if file_type == DataFileType.OutletData:
                self._outlet_data.add_variables(
                    cast(List[Dict[str, str]], df.to_dict("records"))
                )
            elif file_type == DataFileType.StateSummary:
                self._state_summary.add_variables(
                    cast(List[Dict[str, str]], df.to_dict("records"))
                )
            elif file_type == DataFileType.SystemData:
                self.system_data.add_variables(
                    cast(List[Dict[str, str]], df.to_dict("records"))
                )

        if data_file_type is None:
            return

        return dfs.get(data_file_type)

    def get_variable_description(
        self, variable_name: str, data_file_type: DataFileType
    ) -> str:
        df = self.get_variables(data_file_type)

        if df is None:
            return ""

        matches = df[
            (df["variable_name"] == variable_name) | (df["long_name"] == variable_name)
        ]

        if len(matches) == 0:
            return ""

        return cast(str, matches["description"].iloc[0])
