# pyright: reportUnknownMemberType=false

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Union, cast

import bs4
import requests
from bs4.element import NavigableString, Tag

from us_libraries._config import Config
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._scraper.interface import IScrapingService

PUBLIC_LIBRARIES_SURVEY_URL = (
    "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
)

CACHED_URLS_FILE = "urls.json"


class ScrapingService(IScrapingService):
    _config: Config
    _logger: logging.Logger

    def __init__(self, config: Config, logger_factory: ILoggerFactory) -> None:
        self._config = config
        self._logger = logger_factory.get_logger(__name__)

    def scrape_files(self) -> Dict[str, Dict[str, str]]:
        cached_urls_path = Path(f"{self._config.data_dir}/{CACHED_URLS_FILE}")

        if cached_urls_path.exists() and not self._config.should_overwrite_cached_urls:
            self._logger.debug(f"Pulling cached urls from {cached_urls_path}")

            with open(cached_urls_path, "r") as f:
                return json.load(f)

        self._logger.debug("Pulling URLs from web")

        scraped_files = self._scrape_files()

        with open(cached_urls_path, "w") as f:
            self._logger.debug("Dumping scraped URLs")
            json.dump(scraped_files, f)

        return scraped_files

    def _scrape_files(self) -> Dict[str, Dict[str, str]]:
        res = requests.get(
            PUBLIC_LIBRARIES_SURVEY_URL,
        )

        if res.status_code != 200:
            msg = f"Got a non-200 status code for {PUBLIC_LIBRARIES_SURVEY_URL}: {res.status_code}"

            self._logger.exception(msg)
            raise Exception(msg)

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
            raise Exception("this should have matched")

        return match.group(1)
