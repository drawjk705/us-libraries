from abc import ABC
from typing import Optional

from us_pls._download.models import DatafileType
from us_pls._variables.models import Variables


class IVariableRepository(ABC):
    _summary_data_vars: Variables
    _system_data_vars: Variables
    _outlet_data_vars: Variables

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
