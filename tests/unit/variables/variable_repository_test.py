from typing import Tuple

import pandas
import pytest

from tests.service_test_fixtures import ServiceTestFixture
from tests.utils import shuffled_cases
from us_libraries._variables.models import DataFileType
from us_libraries._variables.repository import VariableRepository

extractor_retval = {
    DataFileType.OutletData: pandas.DataFrame(
        [
            dict(variable_name="abc", long_name="alphabet", description="the abcs"),
            dict(
                variable_name="123",
                long_name="numbers",
                description="things that count",
            ),
        ]
    ),
    DataFileType.StateSummary: pandas.DataFrame(
        [
            dict(variable_name="st", long_name="street", description="where I grew up"),
            dict(
                variable_name="mt",
                long_name="mountain",
                description="a large tract of...land",
            ),
        ]
    ),
    DataFileType.SystemData: pandas.DataFrame(
        [
            dict(variable_name="jr", long_name="junior", description="a little guy"),
            dict(variable_name="sr", long_name="senior", description="a big guy"),
        ]
    ),
}


class TestVariableRepository(ServiceTestFixture[VariableRepository]):
    @pytest.mark.parametrize("extractor_returns", [True, False])
    def test_get_variables(self, extractor_returns: bool):
        self.mocker.patch.object(
            self._service._extractor,
            "extract_variables_from_documentation_pdf",
            return_value=extractor_retval if extractor_returns else None,
        )

        res = self._service.get_variables(DataFileType.OutletData)

        if not extractor_returns:
            assert res is None
            self.cast_mock(self._service._logger.info).assert_called_once_with(
                "could not extract any variables from documentation PDF"
            )
        else:
            assert res is not None
            assert extractor_retval[DataFileType.OutletData].to_dict(
                "records"
            ) == res.to_dict("records")

            assert self._service.outlet_data.__dict__ == {
                "alphabet": "alphabet",
                "numbers": "numbers",
            }
            assert self._service.state_summary.__dict__ == {
                "mountain": "mountain",
                "street": "street",
            }
            assert self._service.system_data.__dict__ == {
                "junior": "junior",
                "senior": "senior",
            }

    @pytest.mark.parametrize(
        *shuffled_cases(
            get_variables_returns=[True, False],
            data_file_type=[
                DataFileType.OutletData,
                "other",
            ],
            variable_name_and_expected_description=[
                ("abc", "the abcs"),
                ("numbers", "things that count"),
                ("banana", ""),
            ],
        )
    )
    def test_get_variable_description(
        self,
        get_variables_returns: bool,
        data_file_type: DataFileType,
        variable_name_and_expected_description: Tuple[str, str],
    ):
        self.mocker.patch.object(
            self._service,
            "get_variables",
            return_value=extractor_retval.get(data_file_type)
            if get_variables_returns
            else None,
        )

        variable_name, expected_description = variable_name_and_expected_description

        res = self._service.get_variable_description(variable_name, data_file_type)

        if not get_variables_returns or data_file_type == "other":
            assert res == ""

        else:
            assert res == expected_description
