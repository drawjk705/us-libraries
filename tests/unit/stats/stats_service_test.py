import pandas
import pytest
from callee.strings import EndsWith, String

from tests.service_test_fixtures import ServiceTestFixture
from us_pls._config import Config
from us_pls._download.models import DatafileType
from us_pls._logger.interface import ILoggerFactory
from us_pls._persistence.interface import IOnDiskCache
from us_pls._stats.stats_service import StatsService

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
    def __init__(self, cache: IOnDiskCache, logger_factory: ILoggerFactory) -> None:
        super().__init__(
            config=Config(2018), cache=cache, logger_factory=logger_factory
        )


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
    ):
        mock_cache_get = self.mocker.patch.object(
            self._service._cache, "get", return_value=read_csv_retval
        )

        res = self._service.get_stats(datafile_type)

        mock_cache_get.assert_called_once_with(
            String() & EndsWith(datafile_type.value), "df"
        )

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

    def test_get_stats_given_none(self):
        self.mocker.patch.object(self._service._cache, "get", return_value=None)

        res = self._service.get_stats(DatafileType.OutletData)

        assert res.empty

    def test_read_docs_given_no_docs(
        self,
    ):
        self.mocker.patch.object(self._service, "_documentation", {})
        self.mocker.patch.object(self._service._cache, "get", return_value=None)

        self._service.read_docs(DatafileType.OutletData)

        self.cast_mock(self._service._logger.debug).assert_called_with(
            "No readme exists for this year"
        )

    def test_get_documentation_given_got_it_already(self):
        self.mocker.patch.object(self._service, "_documentation", dict(some="thing"))

        self._service._get_documentation()

        self.cast_mock(self._service._logger.debug).assert_called_with(
            "Already pulled documentation"
        )
