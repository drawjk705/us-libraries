import pytest
from pytest_mock.plugin import MockerFixture

from tests.service_test_fixtures import ServiceTestFixture
from us_pls._config import Config
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._variables.models import Variables
from us_pls._variables.repository import VariableRepository

default_config = Config(2019)

data_dict_2019 = {
    DatafileType.OutletData: Variables(
        var1="code1", parent1=Variables(subCode1="sub_code1", subCode2="sub_code2")
    ),
    DatafileType.SummaryData: Variables(
        var2="code2", parent2=Variables(subCode1="sub_code1", subCode2="sub_code2")
    ),
    DatafileType.SystemData: Variables(
        var3="code3", parent3=Variables(subCode1="sub_code1", subCode2="sub_code2")
    ),
}


@pytest.fixture(autouse=True)
def given_data_dicts(mocker: MockerFixture):
    return mocker.patch(
        "us_pls._variables.repository.DATA_DICTS",
        {2019: data_dict_2019},
    )


class LightVariableRepo(VariableRepository):
    def __init__(self, logger_factory: ILoggerFactory) -> None:
        super().__init__(default_config, logger_factory)


class TestVariableRepo(ServiceTestFixture[LightVariableRepo]):
    pass

    def test_get_data_dict_for_year_given_null_result(self):
        self.mocker.patch.object(self._service._config, "year", 1111)

        res = self._service._get_data_dict_for_year()

        assert res == data_dict_2019
        self.cast_mock(self._service._logger.warning).assert_called_once_with(
            "Could not get variable data for year 1111. Getting variables for 2019 instead"
        )

    def test_get_data_dict_for_year(self):
        res = self._service._get_data_dict_for_year()

        assert res == data_dict_2019
        self.cast_mock(self._service._logger.warning).assert_not_called()

    def test_init_repository(self):
        self._service._init_repository()

        assert self._service.outlet_data_vars == Variables.from_dict(
            {
                "code1": "code1",
                "parent1": {
                    "sub_code1": "parent1_sub_code1",
                    "sub_code2": "parent1_sub_code2",
                },
            }
        )
        assert self._service.summary_data_vars == Variables.from_dict(
            {
                "code2": "code2",
                "parent2": {
                    "sub_code1": "parent2_sub_code1",
                    "sub_code2": "parent2_sub_code2",
                },
            }
        )
        assert self._service.system_data_vars == Variables.from_dict(
            {
                "code3": "code3",
                "parent3": {
                    "sub_code1": "parent3_sub_code1",
                    "sub_code2": "parent3_sub_code2",
                },
            }
        )

    def test_get_variables_for(self):
        assert (
            self._service.get_variables_for(DatafileType.OutletData)
            == data_dict_2019[DatafileType.OutletData]
        )
        assert (
            self._service.get_variables_for(DatafileType.SystemData)
            == data_dict_2019[DatafileType.SystemData]
        )
        assert (
            self._service.get_variables_for(DatafileType.SummaryData)
            == data_dict_2019[DatafileType.SummaryData]
        )
        assert self._service.get_variables_for("banana") == None  # type: ignore
