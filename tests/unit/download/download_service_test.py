import os
import zipfile
from typing import Dict
from unittest.mock import MagicMock, call

import callee
import callee.strings as strings
import pytest
from pytest_mock.plugin import MockerFixture

from tests.service_test_fixtures import ApiServiceTestFixture
from tests.utils import MockRes, shuffled_cases
from us_libraries._config import Config
from us_libraries._download.download_service import DownloadService
from us_libraries._download.models import DownloadType
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._scraper.interface import IScrapingService

config = Config(2020)


@pytest.fixture
def mock_os(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("us_libraries._download.download_service.os")


@pytest.fixture
def mock_zipfile(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(zipfile, "ZipFile")


@pytest.fixture(autouse=True)
def mock_path(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("us_libraries._download.download_service.Path")


class LightDownloadService(DownloadService):
    def __init__(
        self, scraper: IScrapingService, logger_factory: ILoggerFactory
    ) -> None:
        super().__init__(config, scraper, logger_factory)


class TestDownloadService(ApiServiceTestFixture[LightDownloadService]):
    @pytest.mark.parametrize("year_is_scraped", [True, False])
    def test_download_given_year_not_in_scraped_dict(self, year_is_scraped: bool):
        scraper_retval: Dict[str, Dict[str, str]] = (
            {str(config.year): dict(something="here")} if year_is_scraped else dict()
        )

        self.mocker.patch.object(
            self._service._scraper, "scrape_files", return_value=scraper_retval
        )

        mock_try_download = self.mocker.patch.object(
            self._service, "_try_download_resource"
        )

        self._service.download()

        if not year_is_scraped:
            self.cast_mock(self._service._logger.info).assert_called_once_with(
                "There is no data for 2020"
            )
            mock_try_download.assert_not_called()
        else:
            self.cast_mock(self._service._logger.info).assert_not_called()
            mock_try_download.assert_has_calls(
                [
                    call(callee.Dict(), "Documentation", DownloadType.Documentation),
                    call(callee.Dict(), "CSV", DownloadType.CsvZip),
                    call(
                        callee.Dict(),
                        "Data Element Definitions",
                        DownloadType.DataElementDefinitions,
                    ),
                ]
            )

    @pytest.mark.parametrize(
        *shuffled_cases(
            has_resource=[True, False],
            download_type=[
                DownloadType.SystemDataFile,
                DownloadType.StateSummaryAndCharacteristicData,
                DownloadType.OutletData,
            ],
        )
    )
    def test_try_download_resource(
        self, has_resource: bool, download_type: DownloadType
    ):
        resource = "route"
        scraped_dict: Dict[str, str] = (
            dict(resource=resource) if has_resource else dict()
        )
        mock_write_content = self.mocker.patch.object(self._service, "_write_content")
        mock_res_content = "banana"
        self.requests_get_mock.return_value = MockRes(200, mock_res_content)

        self._service._try_download_resource(scraped_dict, "resource", download_type)

        if not has_resource:
            self.cast_mock(self._service._logger.info).assert_called_once_with(
                "The resource `resource` does not exist for 2020"
            )
            self.requests_get_mock.assert_not_called()
            mock_write_content.assert_not_called()
        else:
            self.cast_mock(self._service._logger.info).assert_not_called()
            self.requests_get_mock.assert_called_once_with(
                strings.String() & strings.EndsWith(resource)
            )
            mock_write_content.assert_called_once_with(
                download_type,
                mock_res_content,
                should_unzip=download_type == DownloadType.CsvZip,
            )

    @pytest.mark.parametrize("should_unzip", [True, False])
    def test_write_content(
        self, should_unzip: bool, mock_os: os, mock_zipfile: MagicMock
    ):
        mock_prefix = "prefix"
        self.mocker.patch.object(self._service, "_data_prefix", mock_prefix)
        mock_open = self.mocker.patch("builtins.open")

        path = f"{mock_prefix}/{DownloadType.Documentation.value}"

        mock_move_content = self.mocker.patch.object(self._service, "_move_content")

        self._service._write_content(
            DownloadType.Documentation, b"content", should_unzip
        )

        mock_open.assert_called_once_with(path, "wb")

        if should_unzip:
            mock_zipfile.assert_called_once_with(path, "r")
            mock_move_content.assert_called_once()
            self.cast_mock(mock_os.remove).assert_called_once_with(path)
        else:
            mock_zipfile.assert_not_called()
            mock_move_content.assert_not_called()
            self.cast_mock(mock_os.remove).assert_not_called()
