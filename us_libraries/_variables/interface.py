from abc import ABC, abstractmethod
from typing import Dict, Optional

import pandas as pd

from us_libraries._variables.models import DataFileType, VariableSet


class IVariableExtractionService(ABC):
    @abstractmethod
    def extract_variables_from_documentation_pdf(
        self,
    ) -> Optional[Dict[DataFileType, pd.DataFrame]]:
        ...


class IVariableRepository(ABC):
    _system_data: VariableSet
    _state_summary: VariableSet
    _outlet_data: VariableSet

    @abstractmethod
    def get_variables(
        self, data_file_type: Optional[DataFileType] = None
    ) -> Optional[pd.DataFrame]:
        ...

    @abstractmethod
    def get_variable_description(
        self, variable_name: str, data_file_type: DataFileType
    ) -> str:
        ...

    @property
    def system_data(self) -> VariableSet:
        return self._system_data

    @property
    def state_summary(self) -> VariableSet:
        return self._state_summary

    @property
    def outlet_data(self) -> VariableSet:
        return self._outlet_data
