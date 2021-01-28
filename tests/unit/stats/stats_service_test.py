from unittest.mock import MagicMock

import pandas
import pytest
from callee.strings import EndsWith, String

from tests.service_test_fixtures import ServiceTestFixture
from us_libraries._download.models import DownloadType
from us_libraries._stats.stats_service import StatsService
from us_libraries._variables.models import DataFileType

variable_repo_res = pandas.DataFrame(
    [
        dict(short_name="short1", long_name="long1"),
        dict(short_name="short2", long_name="long2"),
        dict(short_name="short3", long_name="long3"),
        dict(short_name="short4", long_name="long4"),
    ]
)

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


class TestStatsService(ServiceTestFixture[StatsService]):
    @pytest.mark.parametrize(
        "data_file_type, download_type",
        [
            (DataFileType.OutletData, DownloadType.OutletData),
            (DataFileType.StateSummary, DownloadType.StateSummaryAndCharacteristicData),
            (DataFileType.SystemData, DownloadType.SystemData),
        ],
    )
    def test_get_stats_without_variables(
        self,
        data_file_type: DataFileType,
        download_type: DownloadType,
        mock_read_csv: MagicMock,
    ):
        self.mocker.patch.object(
            self._service._variable_repo,
            "get_variables",
            return_value=variable_repo_res,
        )
        mock_read_csv.return_value = read_csv_retval

        res = self._service.get_stats(data_file_type)

        mock_read_csv.assert_called_once_with(String() & EndsWith(download_type.value))

        assert res.to_dict("records") == [
            {
                "long1": "short 1 val 1",
                "long2": "short 2 val 1",
                "long3": "short 3 val 1",
                "long4": "short 4 val 1",
            },
            {
                "long1": "short 1 val 2",
                "long2": "short 2 val 2",
                "long3": "short 3 val 2",
                "long4": "short 4 val 2",
            },
            {
                "long1": "short 1 val 3",
                "long2": "short 2 val 3",
                "long3": "short 3 val 3",
                "long4": "short 4 val 3",
            },
        ]

    @pytest.mark.parametrize(
        "data_file_type",
        [
            DataFileType.OutletData,
            DataFileType.StateSummary,
            DataFileType.SystemData,
        ],
    )
    def test_get_stats_with_variables(
        self,
        data_file_type: DataFileType,
        mock_read_csv: MagicMock,
    ):
        self.mocker.patch.object(
            self._service._variable_repo,
            "get_variables",
            return_value=variable_repo_res,
        )
        mock_read_csv.return_value = read_csv_retval

        res = self._service.get_stats(data_file_type, "long1", "long2")

        assert res.to_dict("records") == [
            {"long1": "short 1 val 1", "long2": "short 2 val 1"},
            {"long1": "short 1 val 2", "long2": "short 2 val 2"},
            {"long1": "short 1 val 3", "long2": "short 2 val 3"},
        ]
