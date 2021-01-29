import zipfile
from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, call

import callee
import callee.strings as strings
import pytest
from pytest_mock.plugin import MockerFixture

from tests.service_test_fixtures import ApiServiceTestFixture
from tests.utils import MockRes, shuffled_cases
from us_pls._config import Config
from us_pls._download.download_service import DownloadService
from us_pls._download.models import DownloadType
from us_pls._logger.interface import ILoggerFactory
from us_pls._persistence.interface import IOnDiskCache
from us_pls._scraper.interface import IScrapingService

config = Config(2020)


@pytest.fixture
def mock_zipfile(mocker: MockerFixture) -> MagicMock:
    return mocker.patch.object(zipfile, "ZipFile")


@pytest.fixture(autouse=True)
def mock_path(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("us_pls._download.download_service.Path")


class LightDownloadService(DownloadService):
    def __init__(
        self,
        scraper: IScrapingService,
        cache: IOnDiskCache,
        logger_factory: ILoggerFactory,
    ) -> None:
        super().__init__(config, scraper, cache, logger_factory)


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
        self.mocker.patch.object(self._service, "_clean_up_readme")

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
            has_urls=[True, False],
            has_resource=[True, False],
            download_type=[
                DownloadType.CsvZip,
                DownloadType.Documentation,
                DownloadType.DataElementDefinitions,
            ],
        )
    )
    def test_try_download_resource(
        self, has_urls: bool, has_resource: bool, download_type: DownloadType
    ):
        resource = "route"
        scraped_dict: Dict[str, str] = dict(resource=resource) if has_urls else dict()
        mock_write_content = self.mocker.patch.object(self._service, "_write_content")
        mock_res_content = "banana"
        self.requests_get_mock.return_value = MockRes(200, mock_res_content)
        self.mocker.patch.object(
            self._service, "_resource_already_exists", return_value=has_resource
        )

        self._service._try_download_resource(scraped_dict, "resource", download_type)

        if not has_urls:
            self.cast_mock(self._service._logger.warning).assert_called_once_with(
                "The resource `resource` does not exist for 2020"
            )
            self.requests_get_mock.assert_not_called()
            mock_write_content.assert_not_called()
        else:
            if has_resource:
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
    def test_write_content(self, should_unzip: bool, mock_zipfile: MagicMock):
        self.mocker.patch.object(Path, "is_dir", return_value=False)
        self.mocker.patch.object(
            self._service._cache.cache_path, "iterdir", return_value=[Path()]
        )

        self._service._write_content(
            DownloadType.Documentation, b"content", should_unzip
        )

        self.cast_mock(self._service._cache.put).assert_called_once_with(
            b"content", DownloadType.Documentation.value
        )

        if should_unzip:
            mock_zipfile.assert_called_once()
            self.cast_mock(self._service._cache.rename).assert_called_once()
            self.cast_mock(self._service._cache.remove).assert_called_once()
        else:
            mock_zipfile.assert_not_called()
            self.cast_mock(self._service._cache.rename).assert_not_called()
            self.cast_mock(self._service._cache.remove).assert_not_called()
