import logging
from typing import Dict, Optional

from us_pls._config import Config
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._variables._data_dicts import DATA_DICTS
from us_pls._variables.interface import IVariableRepository
from us_pls._variables.models import Variables


class VariableRepository(IVariableRepository):
    _config: Config
    _logger: logging.Logger

    _data_dict: Dict[DatafileType, Variables]

    # inherited from parent
    _outlet_data_vars: Variables
    _summary_data_vars: Variables
    _system_data_vars: Variables

    def __init__(self, config: Config, logger_factory: ILoggerFactory) -> None:
        self._config = config
        self._logger = logger_factory.get_logger(__name__)

        self._init_repository()

    def get_variables_for(self, datafile_type: DatafileType) -> Optional[Variables]:
        return self._data_dict.get(datafile_type)

    def _init_repository(self) -> None:
        self._data_dict = self._get_data_dict_for_year()

        self._summary_data_vars = self._data_dict.get(
            DatafileType.SummaryData, Variables()
        )
        self._system_data_vars = self._data_dict.get(
            DatafileType.SystemData, Variables()
        )
        self._outlet_data_vars = self._data_dict.get(
            DatafileType.OutletData, Variables()
        )

    def _get_data_dict_for_year(self) -> Dict[DatafileType, Variables]:
        dict_res = DATA_DICTS.get(self._config.year)

        if dict_res is not None:
            return dict_res

        max_key = max(DATA_DICTS.keys())

        self._logger.warning(
            f"Could not get variable data for year {self._config.year}. Getting variables for {max_key} instead"
        )

        return DATA_DICTS[max_key]
