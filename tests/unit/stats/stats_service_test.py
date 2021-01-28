from unittest.mock import MagicMock

import pandas
import pytest
from callee.strings import EndsWith, String

from tests.service_test_fixtures import ServiceTestFixture
from us_libraries._config import Config
from us_libraries._download.models import DatafileType
from us_libraries._stats.stats_service import StatsService

read_csv_retval = pandas.DataFrame(
    [
        dict(
            short1="short 1 val 1",
            short2="short 2 val 1",
            short3="short 3 val 1",
            short4="short 4 val 1",
        ),
        dict(
            short1="short 1 val 2",
            short2="short 2 val 2",
            short3="short 3 val 2",
            short4="short 4 val 2",
        ),
        dict(
            short1="short 1 val 3",
            short2="short 2 val 3",
            short3="short 3 val 3",
            short4="short 4 val 3",
        ),
    ]
)


class LightStatsService(StatsService):
    def __init__(self) -> None:
        super().__init__(config=Config(2018))


class TestStatsService(ServiceTestFixture[LightStatsService]):
    @pytest.mark.parametrize(
        "datafile_type",
        [
            DatafileType.OutletData,
            DatafileType.StateSummaryAndCharacteristicData,
            DatafileType.SystemData,
        ],
    )
    def test_get_stats(
        self,
        datafile_type: DatafileType,
        mock_read_csv: MagicMock,
    ):
        mock_read_csv.return_value = read_csv_retval

        res = self._service._get_stats(datafile_type)

        mock_read_csv.assert_called_once_with(String() & EndsWith(datafile_type.value))

        assert res.to_dict("records") == [
            {
                "short1": "short 1 val 1",
                "short2": "short 2 val 1",
                "short3": "short 3 val 1",
                "short4": "short 4 val 1",
            },
            {
                "short1": "short 1 val 2",
                "short2": "short 2 val 2",
                "short3": "short 3 val 2",
                "short4": "short 4 val 2",
            },
            {
                "short1": "short 1 val 3",
                "short2": "short 2 val 3",
                "short3": "short 3 val 3",
                "short4": "short 4 val 3",
            },
        ]
