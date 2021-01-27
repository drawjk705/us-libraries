# pyright: reportUnknownMemberType=false

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, cast

import pandas as pd
import pdfminer.high_level as pdf
import tabula
from pdfminer.layout import LTPage, LTTextContainer

from us_libraries._cache.interface import IOnDiskCache
from us_libraries._config import Config
from us_libraries._download.models import DownloadType
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._variables.interface import IVariableExtractionService
from us_libraries._variables.models import DataFileType

EXTRACTED_VARIABLES_RESOURCE = "extracted_variables.csv"

STATE_SUMMARY_APPENDIX_NAME = (
    "Record Layout for Public Library State Summary/ State Characteristics Data File"
)
SYSTEM_DATA_APPENDIX_NAME = "Record Layout for Public Library System Data File"
OUTLET_DATA_APPENDIX_NAME = "Record Layout for Public Library Outlet Data File"


class VariableExtractionService(IVariableExtractionService):
    _cache: IOnDiskCache
    _config: Config
    _logger: logging.Logger

    def __init__(
        self, cache: IOnDiskCache, config: Config, logger_factory: ILoggerFactory
    ) -> None:
        self._cache = cache
        self._config = config
        self._logger = logger_factory.get_logger(__name__)

    def extract_variables_from_documentation_pdf(
        self,
    ) -> Optional[Dict[DataFileType, pd.DataFrame]]:
        has_pulled_all_vars = True

        extracted_variables: Dict[DataFileType, pd.DataFrame] = {}

        for data_file_type in DataFileType:
            res = self._cache.get(f"{data_file_type.value}.csv")

            if res.empty:
                has_pulled_all_vars = False
                break

            extracted_variables[data_file_type] = res

        if has_pulled_all_vars:
            return extracted_variables

        documentation_file = Path(
            f"{self._config.data_dir}/{self._config.year}/{DownloadType.Documentation.value}"
        )

        if not documentation_file.exists():
            self._logger.info(f"no documentation file at `{documentation_file}`!")
            return None

        page_mappings = self._find_pages_with_tables(documentation_file)

        for data_file_type, pages in page_mappings.items():
            str_pages = ",".join([str(page) for page in pages])

            pdf_dfs: List[pd.DataFrame] = tabula.read_pdf(
                documentation_file, pages=str_pages
            )

            all_vars = pd.DataFrame()

            for df in pdf_dfs:
                columns = df.columns.tolist()

                if "Data" not in columns:
                    continue

                first_col = columns[0]
                last_col = columns[-1]

                column_remapping = {first_col: "variable_name", last_col: "description"}

                filtered_df = df.dropna(subset=[first_col, last_col])  # type: ignore

                renamed_df: pd.DataFrame = filtered_df.rename(columns=column_remapping)  # type: ignore
                smaller_df = renamed_df[["variable_name", "description"]]

                if all_vars.empty:
                    all_vars = smaller_df
                else:
                    all_vars = all_vars.append(smaller_df, ignore_index=True)

                df_to_store = all_vars.reset_index(drop=True)

                df_to_store["long_name"] = df_to_store["description"].apply(
                    self._make_variable_name
                )

                self._cache.put(f"{data_file_type.value}.csv", df_to_store)

                extracted_variables[data_file_type] = df_to_store

        return extracted_variables

    def _find_pages_with_tables(self, file_path: Path) -> Dict[DataFileType, List[int]]:

        state_summary_pages: List[int] = []
        system_data_pages: List[int] = []
        outlet_data_pages: List[int] = []

        for page_num, page in enumerate(
            cast(List[LTPage], pdf.extract_pages(file_path))
        ):
            for element in page:  # type: ignore
                if not isinstance(element, LTTextContainer):
                    continue
                text: str = element.get_text()

                if STATE_SUMMARY_APPENDIX_NAME in text:
                    state_summary_pages.append(page_num)
                if SYSTEM_DATA_APPENDIX_NAME in text:
                    system_data_pages.append(page_num)
                if OUTLET_DATA_APPENDIX_NAME in text:
                    outlet_data_pages.append(page_num)

        return {
            DataFileType.StateSummary: state_summary_pages,
            DataFileType.SystemData: system_data_pages,
            DataFileType.OutletData: outlet_data_pages,
        }

    def _make_variable_name(self, variable_description: str) -> str:
        first_chunk = re.split(r"[.,!?()]", variable_description)[0]

        return "_".join(
            [
                word.strip().capitalize()
                for word in first_chunk.replace("-", " ").strip().split(" ")
            ]
        )
