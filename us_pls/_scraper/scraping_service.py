# pyright: reportUnknownMemberType=false

import logging
import re
from typing import Dict, List, Union, cast

import bs4
import requests
from bs4.element import NavigableString, Tag

from us_pls._config import Config
from us_pls._logger.interface import ILoggerFactory
from us_pls._persistence.interface import IOnDiskCache
from us_pls._scraper.interface import IScrapingService

PUBLIC_LIBRARIES_SURVEY_URL = (
    "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
)

CACHED_URLS_FILE = "../urls.json"


class ScrapingService(IScrapingService):
    _config: Config
    _logger: logging.Logger
    _cache: IOnDiskCache

    def __init__(
        self, config: Config, logger_factory: ILoggerFactory, cache: IOnDiskCache
    ) -> None:
        self._config = config
        self._logger = logger_factory.get_logger(__name__)
        self._cache = cache

    def scrape_files(self) -> Dict[str, Dict[str, str]]:
        cached_urls = self._cache.get(CACHED_URLS_FILE, "json")

        if cached_urls is not None and not self._config.should_overwrite_cached_urls:
            return cached_urls

        self._logger.debug("Pulling URLs from web")

        scraped_files = self._scrape_files()

        self._cache.put(scraped_files, CACHED_URLS_FILE)

        return scraped_files

    def _scrape_files(self) -> Dict[str, Dict[str, str]]:
        res = requests.get(
            PUBLIC_LIBRARIES_SURVEY_URL,
        )

        if res.status_code != 200:
            msg = f"Got a non-200 status code for {PUBLIC_LIBRARIES_SURVEY_URL}: {res.status_code}"

            self._logger.exception(msg)
            raise ScraperException(msg)

        soup = bs4.BeautifulSoup(res.content, "html.parser")

        url_dict: Dict[str, Dict[str, str]] = {}

        for tag in cast(
            List[Tag], soup.find_all("label", attrs={"for": re.compile(r"FY \d{4}")})
        ):
            year = self._get_year_for_data(cast(str, tag["for"]))

            url_dict[year] = {}

            for sib in cast(List[Union[Tag, NavigableString]], tag.next_siblings):
                if isinstance(sib, NavigableString):
                    continue

                for anchor_tag in cast(List[Tag], sib.find_all("a")):
                    href: str = anchor_tag["href"]
                    text: str = anchor_tag.text

                    text = " ".join(text.replace("\n", " ").split())

                    url_dict[year][text] = href

        return url_dict

    def _get_year_for_data(self, year_text: str) -> str:
        match = re.match(r"FY (\d{4})", year_text)

        if not match:
            raise ScraperException("this should have matched")

        return match.group(1)


class ScraperException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
