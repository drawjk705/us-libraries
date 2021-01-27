from abc import ABC, abstractmethod

import pandas as pd

from us_libraries._variables.models import VariableSet


class IVariableExtractionService(ABC):
    @abstractmethod
    def extract_variables_from_documentation_pdf(self) -> None:
        ...


class IVariableRepository(ABC):
    _variables: VariableSet

    @abstractmethod
    def get_variables(self) -> pd.DataFrame:
        ...

    @abstractmethod
    def get_variable_description(self, variable_name: str) -> str:
        ...

    @property
    def variables(self) -> VariableSet:
        return self._variables
