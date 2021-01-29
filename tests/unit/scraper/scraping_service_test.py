import json
from typing import Dict
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from tests.service_test_fixtures import ServiceTestFixture
from tests.utils import shuffled_cases
from us_pls._scraper.scraping_service import ScrapingService

patch_path_prefix = "us_pls._scraper.scraping_service"


@pytest.fixture
def mock_path(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(f"{patch_path_prefix}.Path")


@pytest.fixture
def mock_json(mocker: MockerFixture) -> MagicMock:
    return mocker.patch(f"{patch_path_prefix}.json")


@pytest.fixture
def mock_open(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("builtins.open")


class TestScrapingService(ServiceTestFixture[ScrapingService]):
    @pytest.mark.parametrize(
        *shuffled_cases(
            urls_are_in_cache=[True, False], should_overwrite_cached_urls=[True, False]
        )
    )
    def test_scrape_files(
        self,
        urls_are_in_cache: bool,
        should_overwrite_cached_urls: bool,
        mock_path: MagicMock,
        mock_json: json,
        mock_open: MagicMock,
    ):
        mock_retval: Dict[str, str] = dict(banana="phone")

        # since we don't want to test BeautifulSoup
        self.mocker.patch.object(
            self._service, "_scrape_files", return_value=mock_retval
        )
        self.mocker.patch.object(
            self._service._config,
            "should_overwrite_cached_urls",
            should_overwrite_cached_urls,
        )
        self.cast_mock(mock_path().exists).return_value = urls_are_in_cache
        self.cast_mock(mock_json.load).return_value = mock_retval

        res = self._service.scrape_files()

        assert res == mock_retval

        if urls_are_in_cache and not should_overwrite_cached_urls:
            mock_open.assert_called_once()
            assert mock_open.call_args_list[0][0][1] == "r"
            self.cast_mock(mock_json.load).assert_called_once()
        else:
            mock_open.assert_called_once()
            assert mock_open.call_args_list[0][0][1] == "w"
            self.cast_mock(mock_json.dump).assert_called_once()

    def test_get_year_for_data(self):
        year_text = "FY 1234"

        assert self._service._get_year_for_data(year_text) == "1234"

    def test_get_year_for_data_given_bad_input(self):
        year_text = "banana"

        with pytest.raises(Exception, match="this should have matched"):
            self._service._get_year_for_data(year_text)
