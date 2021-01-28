from enum import Enum
from typing import Dict, List


class VariableSet:
    def __init__(self) -> None:
        ...

    def add_variables(self, df_records: List[Dict[str, str]]):
        for mapping in df_records:
            long_name = mapping["long_name"]

            self.__setattr__(long_name, long_name)


class DataFileType(Enum):
    SystemData = "system_data"
    StateSummary = "state_summary"
    OutletData = "outlet_data"
