from typing import Dict

from us_pls._download.models import DatafileType
from us_pls._variables.fy2018 import outlet_data_vars as outlet
from us_pls._variables.fy2018 import state_summary_data_vars as state
from us_pls._variables.fy2018 import system_data_vars as system
from us_pls._variables.models import Variables

DATA_DICTS: Dict[int, Dict[DatafileType, Variables]] = {
    2018: {
        DatafileType.SummaryData: state.STATE_SUMMARY_DATA_VARIABLES,
        DatafileType.SystemData: system.SYSTEM_DATA_VARIABLES,
        DatafileType.OutletData: outlet.OUTLET_DATA_VARIABLES,
    }
}
