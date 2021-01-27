# # pyright: reportUnknownMemberType=false

# from us_libraries._variables.models import DataFileType
# import pdfminer.high_level as pdf
# from pdfminer.layout import LTTextContainer
# from typing import Dict, List, Tuple, cast
# from us_libraries._resource_mapping.models import ResourceType
# from us_libraries._cache.interface import IOnDiskCache
# import pandas as pd
# from us_libraries._variables.interface import IVariableExtractionService
# from us_libraries._resource_mapping.interface import IResourceMappingService
# from us_libraries._config import Config
# import tabula

# EXTRACTED_VARIABLES_RESOURCE = "extracted_variables.csv"


# class VariableExtractionService(IVariableExtractionService):
#     _cache: IOnDiskCache
#     _resource_mapper: IResourceMappingService
#     _config: Config

#     def __init__(
#         self,
#         cache: IOnDiskCache,
#         resource_mapper: IResourceMappingService,
#         config: Config,
#     ) -> None:
#         self._cache = cache
#         self._resource_mapper = resource_mapper
#         self._config = config

#     def extract_variables_from_pdf(self) -> pd.DataFrame:
#         cache_res = self._cache.get(EXTRACTED_VARIABLES_RESOURCE)

#         if not cache_res.empty:
#             return cache_res

#         file_prefix = f"{self._config.data_dir}/{self._config.year}"
#         pdf_file_name = cast(
#             Tuple[str, ...],
#             self._resource_mapper.get_resource_paths(
#                 for_resource=ResourceType.Documentation
#             ),
#         )[0]

#         pdf_dfs: List[pd.DataFrame] = tabula.read_pdf(
#             f"{file_prefix}/{pdf_file_name}", pages="all"
#         )

#         all_vars = pd.DataFrame()

#         for df in pdf_dfs:
#             columns = df.columns.tolist()

#             if "Data" not in columns:
#                 continue

#             first_col = columns[0]
#             last_col = columns[-1]

#             column_remapping = {first_col: "variable_name", last_col: "description"}

#             filtered_df = df.dropna(subset=[first_col, last_col])  # type: ignore

#             renamed_df: pd.DataFrame = filtered_df.rename(columns=column_remapping)  # type: ignore
#             smaller_df = renamed_df[["variable_name", "description"]]

#             if all_vars.empty:
#                 all_vars = smaller_df
#             else:
#                 all_vars = all_vars.append(smaller_df, ignore_index=True)

#         df_to_return = all_vars.reset_index(drop=True)

#         self._cache.put(EXTRACTED_VARIABLES_RESOURCE, df_to_return)

#         return df_to_return

#     def _find_pages_with_tables(self) -> Dict[DataFileType: List[int]]:
#         state_summary_appendix_name = "Record Layout for Public Library State Summary/ State Characteristics Data File"
#         system_data_appendix_name = "Record Layout for Public Library System Data File"
#         outlet_data_appendix_name = "Record Layout for Public Library Outlet Data File"

#         state_summary_pages = []
#         system_data_pages = []
#         outlet_data_pages = []

#         for page in pdf.extract_pages(f'{self._config.data_dir}/{self._config.year}/{}')
