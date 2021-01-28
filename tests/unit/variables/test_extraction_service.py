# pyright: reportUnknownMemberType=false

from pathlib import Path
from typing import Generator, List
from unittest.mock import MagicMock, call

import pandas
import pdfminer.high_level as pdf
import pytest
import tabula
from pdfminer.layout import LTTextContainer
from pytest_mock.plugin import MockerFixture

from tests.service_test_fixtures import ServiceTestFixture
from tests.utils import DataFrameMatcher, shuffled_cases
from us_libraries._cache.interface import IOnDiskCache
from us_libraries._config import Config
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._variables.extraction_service import VariableExtractionService
from us_libraries._variables.models import DataFileType


class _MockLTTextContainer(LTTextContainer):
    _text: str

    def __init__(self, text: str) -> None:
        self._text = text

    def get_text(self) -> str:
        return self._text


class _MockLTPage:
    _elements: List[_MockLTTextContainer]

    def __init__(self, element_texts: List[str]) -> None:
        self._elements = [_MockLTTextContainer(text) for text in element_texts]

    def __iter__(self) -> Generator[_MockLTTextContainer, None, None]:
        for element in self._elements:
            yield element


mock_config = Config(2020)


@pytest.fixture
def mock_path(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("us_libraries._variables.extraction_service.Path")


class LightVariableExtractionService(VariableExtractionService):
    def __init__(self, cache: IOnDiskCache, logger_factory: ILoggerFactory) -> None:
        super().__init__(cache, mock_config, logger_factory)


class TestVariableExtractionService(ServiceTestFixture[LightVariableExtractionService]):
    def test_find_pages_with_tables(self):
        mock_pages = [
            _MockLTPage(["banana"]),
            _MockLTPage(
                [
                    "apple",
                    "aaaRecord Layout for Public Library State Summary/ State Characteristics Data Filebbb",
                ]
            ),
            _MockLTPage(
                ["orange", "xxxRecord Layout for Public Library System Data Filexxxx"]
            ),
            _MockLTPage(
                [
                    "grape",
                    "aaaRecord Layout for Public Library Outlet Data Filebbb",
                    "peach",
                ]
            ),
        ]

        self.mocker.patch.object(pdf, "extract_pages", return_value=mock_pages)

        res = self._service._find_pages_with_tables(Path())

        assert res == {
            DataFileType.SystemData: [2],
            DataFileType.StateSummary: [1],
            DataFileType.OutletData: [3],
        }

    @pytest.mark.parametrize(
        *shuffled_cases(
            has_pulled_all_vars=[True, False], documentation_file_exists=[True, False]
        )
    )
    def test_extract_variables_from_documentation_pdf(
        self,
        has_pulled_all_vars: bool,
        documentation_file_exists: bool,
        mock_path: MagicMock,
    ):
        mock_path().exists.return_value = documentation_file_exists
        mock_cache_res = (
            pandas.DataFrame([dict(something="here")])
            if has_pulled_all_vars
            else pandas.DataFrame()
        )
        find_pages_with_tables_res = {
            DataFileType.StateSummary: [1, 2, 3],
            DataFileType.OutletData: [4, 5, 6],
            DataFileType.SystemData: [7, 8, 9],
        }
        read_pdf_side_effects = [
            [
                pandas.DataFrame(
                    [
                        dict(
                            fruit="banana",
                            something="random",
                            Data="data",
                            last="a yellow fruit",
                        )
                    ]
                ),
            ],
            [
                pandas.DataFrame(
                    [
                        dict(
                            vegetable="lettuce",
                            something="random",
                            something_else="should skip",
                            last="a leafy veggie",
                        )
                    ]
                )
            ],
            [
                pandas.DataFrame(
                    [
                        dict(
                            fruit="apple",
                            something="random",
                            Data="data",
                            last="a round-ish fruit",
                        ),
                    ]
                ),
                pandas.DataFrame(
                    [
                        dict(
                            fruit="orange",
                            something="random",
                            Data="data",
                            last="an orange fruit",
                        ),
                    ]
                ),
            ],
        ]

        self.mocker.patch.object(
            self._service._cache, "get", return_value=mock_cache_res
        )
        mock_find_pages_with_tables = self.mocker.patch.object(
            self._service,
            "_find_pages_with_tables",
            return_value=find_pages_with_tables_res,
        )
        mock_read_pdf = self.mocker.patch.object(
            tabula, "read_pdf", side_effect=read_pdf_side_effects
        )

        self._service.extract_variables_from_documentation_pdf()

        if has_pulled_all_vars or not documentation_file_exists:
            mock_find_pages_with_tables.assert_not_called()
            mock_read_pdf.assert_not_called()

        else:
            self.cast_mock(self._service._cache.put).assert_has_calls(
                [
                    call(
                        "state_summary.csv",
                        DataFrameMatcher(
                            [
                                {
                                    "variable_name": "banana",
                                    "description": "a yellow fruit",
                                    "long_name": "A_Yellow_Fruit",
                                }
                            ]
                        ),
                    ),
                    call(
                        "system_data.csv",
                        DataFrameMatcher(
                            [
                                {
                                    "variable_name": "apple",
                                    "description": "a round-ish fruit",
                                    "long_name": "A_Round_Ish_Fruit",
                                }
                            ]
                        ),
                    ),
                    call(
                        "system_data.csv",
                        DataFrameMatcher(
                            [
                                {
                                    "variable_name": "apple",
                                    "description": "a round-ish fruit",
                                    "long_name": "A_Round_Ish_Fruit",
                                },
                                {
                                    "variable_name": "orange",
                                    "description": "an orange fruit",
                                    "long_name": "An_Orange_Fruit",
                                },
                            ]
                        ),
                    ),
                ]
            )
