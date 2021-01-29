from typing import Dict

import pytest

from tests.service_test_fixtures import ServiceTestFixture
from tests.utils import shuffled_cases
from us_pls._scraper.scraping_service import ScrapingService


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
    ):
        mock_retval: Dict[str, str] = dict(banana="phone")

        self.cast_mock(self._service._cache.get).return_value = (
            mock_retval if urls_are_in_cache else None
        )

        # since we don't want to test BeautifulSoup
        self.mocker.patch.object(
            self._service, "_scrape_files", return_value=mock_retval
        )
        self.mocker.patch.object(
            self._service._config,
            "should_overwrite_cached_urls",
            should_overwrite_cached_urls,
        )

        res = self._service.scrape_files()

        assert res == mock_retval

        if urls_are_in_cache and not should_overwrite_cached_urls:
            self.cast_mock(self._service._cache.put).assert_not_called()
            self.cast_mock(self._service._cache.get).assert_called_once()
        else:
            self.cast_mock(self._service._cache.put).assert_called_once()

    def test_get_year_for_data(self):
        year_text = "FY 1234"

        assert self._service._get_year_for_data(year_text) == "1234"

    def test_get_year_for_data_given_bad_input(self):
        year_text = "banana"

        with pytest.raises(Exception, match="this should have matched"):
            self._service._get_year_for_data(year_text)
