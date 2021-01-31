import logging
from typing import Set

import pandas as pd

from us_pls._config import Config
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._transformer.interface import ITransformationService
from us_pls._variables.interface import IVariableRepository
from us_pls._variables.models import Variables


class TransformationService(ITransformationService):
    _config: Config
    _variable_repo: IVariableRepository
    _logger: logging.Logger

    def __init__(
        self,
        config: Config,
        variable_repo: IVariableRepository,
        logger_factory: ILoggerFactory,
    ) -> None:
        self._config = config
        self._variable_repo = variable_repo
        self._logger = logger_factory.get_logger(__name__)

    def transform_columns(
        self, df: pd.DataFrame, datafile_type: DatafileType
    ) -> pd.DataFrame:
        self._logger.debug(f"Tranformation columns for {datafile_type.value}")

        column_mapping = (
            self._variable_repo.get_variables_for(datafile_type) or Variables()
        )

        renamed_df: pd.DataFrame = df.rename(columns=column_mapping.flatten_and_invert())  # type: ignore

        if renamed_df.columns.tolist() != list(column_mapping.values()):
            self._logger.warning(
                "Not all columns were successfully remapped. See log file for more details."
            )

            self._log_columns_diff(
                set(renamed_df.columns.tolist()),
                set(df.columns.tolist()),
                set([str(key) for key in column_mapping.keys()]),
            )

        return renamed_df

    def _log_columns_diff(
        self, renamed_cols: Set[str], original_cols: Set[str], cols_to_rename: Set[str]
    ) -> None:
        cols_not_renamed = sorted(list(renamed_cols.intersection(original_cols)))
        mappings_not_used_to_rename = sorted(list(cols_to_rename - original_cols))

        self._logger.debug(
            f"The following columns were not renamed: {cols_not_renamed}"
        )
        self._logger.debug(
            f"The following mappings were not used to rename any columns: {mappings_not_used_to_rename}"
        )
