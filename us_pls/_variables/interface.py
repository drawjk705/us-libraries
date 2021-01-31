from abc import ABC
from typing import Dict, Optional

from us_pls._download.models import DatafileType
from us_pls._variables.models import Variables


class IVariableRepository(ABC):
    _summary_data_vars: Variables
    _system_data_vars: Variables
    _outlet_data_vars: Variables

    _new_col_to_original_col_mapping: Dict[DatafileType, Dict[str, str]]

    def get_variables_for(self, datafile_type: DatafileType) -> Optional[Variables]:
        ...

    @property
    def summary_data_vars(self) -> Variables:
        return self._summary_data_vars

    @property
    def system_data_vars(self) -> Variables:
        return self._system_data_vars

    @property
    def outlet_data_vars(self) -> Variables:
        return self._outlet_data_vars

    @property
    def new_col_to_original_col_mapping(self) -> Dict[DatafileType, Dict[str, str]]:
        return self._new_col_to_original_col_mapping
