# # pyright: reportUnknownMemberType=false


# import re
# from typing import cast

# from us_libraries._variables.interface import (
#     IVariableExtractionService,
#     IVariableRepository,
# )
# from us_libraries._variables.models import VariableSet


# class VariableRepository(IVariableRepository):
#     _variables: VariableSet

#     _extraction_service: IVariableExtractionService

#     def __init__(self, extraction_service: IVariableExtractionService) -> None:
#         self._extraction_service = extraction_service

#     def get_variables(self):
#         df = self._extraction_service.extract_variables_from_documentation_pdf()

#         df["short_name"] = df["description"].apply(self._make_variable_name)

#         records = df.to_dict("records")

#         self._variables.add_variables(records)

#         return df

#     def get_variable_description(self, variable_name: str) -> str:
#         variables_df = self.get_variables()

#         matches = variables_df[
#             (variables_df["variable_name"] == variable_name)
#             | (variables_df["short_name"] == variable_name)
#         ]

#         if len(matches) == 0:
#             return ""

#         return cast(str, matches["description"].iloc[0])

#     def _make_variable_name(self, variable_description: str) -> str:
#         first_chunk = re.split(r"[.,!?()]", variable_description)[0]

#         return "_".join(
#             [word.strip().capitalize() for word in first_chunk.strip().split(" ")]
#         )
