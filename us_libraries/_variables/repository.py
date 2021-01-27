# pyright: reportUnknownMemberType=false


import logging
from typing import Dict, List, cast

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

    _extraction_service: IVariableExtractionService
    _logger: logging.Logger

    def __init__(
        self,
        extraction_service: IVariableExtractionService,
        logger_factory: ILoggerFactory,
    ) -> None:
        self._extraction_service = extraction_service
        self._logger = logger_factory.get_logger(__name__)

        self._system_data = VariableSet()
        self._state_summary = VariableSet()
        self._outlet_data = VariableSet()

    def get_variables(self) -> Dict[DataFileType, pd.DataFrame]:
        dfs = self._extraction_service.extract_variables_from_documentation_pdf()

        if not dfs:
            self._logger.info("could not extract any variables from documentation PDF")
            return {}

        for data_file_type, df in dfs.items():
            if data_file_type == DataFileType.OutletData:
                self._outlet_data.add_variables(
                    cast(List[Dict[str, str]], df.to_dict("records"))
                )
            elif data_file_type == DataFileType.StateSummary:
                self._state_summary.add_variables(
                    cast(List[Dict[str, str]], df.to_dict("records"))
                )
            elif data_file_type == DataFileType.SystemData:
                self.system_data.add_variables(
                    cast(List[Dict[str, str]], df.to_dict("records"))
                )

        return dfs

    def get_variable_description(
        self, variable_name: str, data_file_type: DataFileType
    ) -> str:
        variables_df = self.get_variables()[data_file_type]

        matches = variables_df[
            (variables_df["variable_name"] == variable_name)
            | (variables_df["short_name"] == variable_name)
        ]

        if len(matches) == 0:
            return ""

        return cast(str, matches["description"].iloc[0])
