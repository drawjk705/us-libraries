from unittest.mock import call

import pandas as pd

from tests.service_test_fixtures import ServiceTestFixture
from us_pls._config import Config
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._transformer.transformation_service import TransformationService
from us_pls._variables.interface import IVariableRepository
from us_pls._variables.models import Variables

default_config = Config(2019)


class LightTransformationService(TransformationService):
    def __init__(
        self, variable_repo: IVariableRepository, logger_factory: ILoggerFactory
    ) -> None:
        super().__init__(default_config, variable_repo, logger_factory)


class TestTransformationService(ServiceTestFixture[LightTransformationService]):
    def test_transform_columns(self):
        repo_res = Variables(var1="code1", var2="code2")
        df = pd.DataFrame(
            [dict(var1="val1", var2="val2"), dict(var1="var3", var2="val4")]
        )

        self.mocker.patch.object(
            self._service._variable_repo, "get_variables_for", return_value=repo_res
        )

        res = self._service.transform_columns(df, DatafileType.OutletData)

        assert res.to_dict("records") == [
            {"code1": "val1", "code2": "val2"},
            {"code1": "var3", "code2": "val4"},
        ]
        self.cast_mock(self._service._logger.warning).assert_not_called()

    def test_transform_columns_given_imperfect_match(self):
        repo_res = Variables(var1="code1", var2="code2", var3="code3", var4="code4")
        df = pd.DataFrame(
            [
                dict(var1="val1", var2="val2", banana3="banana_val1"),
                dict(var1="var3", var2="val4", banana3="banana_val2"),
            ]
        )
        self.mocker.patch.object(
            self._service._variable_repo, "get_variables_for", return_value=repo_res
        )

        res = self._service.transform_columns(df, DatafileType.OutletData)

        assert res.to_dict("records") == [
            {"banana3": "banana_val1", "code1": "val1", "code2": "val2"},
            {"banana3": "banana_val2", "code1": "var3", "code2": "val4"},
        ]
        self.cast_mock(self._service._logger.warning).assert_called_once_with(
            "Not all columns were successfully remapped. See log file for more details."
        )
        assert self.cast_mock(self._service._logger.debug).call_args_list == [
            call("Tranformation columns for OutletData.csv"),
            call("The following columns were not renamed: ['banana3']"),
            call(
                "The following mappings were not used to rename any columns: ['var3', 'var4']"
            ),
        ]
