from enum import Enum
from typing import Dict, List


class VariableSet:
    def __init__(self) -> None:
        ...

    def add_variables(self, description_to_variable: List[Dict[str, str]]):
        for mapping in description_to_variable:
            short_name = mapping["short_name"]
            variable = mapping["variable_name"]

            self.__setattr__(short_name, variable)


class DataFileType(Enum):
    SystemData = "system_data"
    StateSummary = "state_summary"
    OutletData = "outlet_data"
