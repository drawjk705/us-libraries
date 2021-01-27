# pyright: reportUnknownMemberType=false

import json
import re
from pathlib import Path
from typing import Dict, List, Union, cast

import bs4
import requests
from bs4.element import NavigableString, Tag

from us_libraries._config import Config
from us_libraries._scraper.interface import IScrapingService

PUBLIC_LIBRARIES_SURVEY_URL = (
    "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
)

CACHED_URLS_FILE = "urls.json"


class ScrapingService(IScrapingService):
    _config: Config

    def __init__(self, config: Config) -> None:
        self._config = config

    def scrape_files(self) -> Dict[str, Dict[str, str]]:
        cached_urls_path = Path(f"{self._config.data_dir}/{CACHED_URLS_FILE}")

        if cached_urls_path.exists() and not self._config.should_overwrite_cached_urls:
            with open(cached_urls_path, "r") as f:
                return json.load(f)

        scraped_files = self._scrape_files()

        with open(cached_urls_path, "w") as f:
            json.dump(scraped_files, f)

        return scraped_files

    def _scrape_files(self) -> Dict[str, Dict[str, str]]:
        res = requests.get(PUBLIC_LIBRARIES_SURVEY_URL)  # type: ignore

        soup = bs4.BeautifulSoup(res.content, "html.parser")

        url_dict: Dict[str, Dict[str, str]] = {}

        for tag in cast(
            List[Tag], soup.find_all("label", text=re.compile(r"FY \d{4}"))
        ):
            year = self._get_year_for_data(cast(str, tag.text))

            url_dict[year] = {}

            for sib in cast(List[Union[Tag, NavigableString]], tag.next_siblings):
                if isinstance(sib, NavigableString):
                    continue

                for anchor_tag in cast(List[Tag], sib.find_all("a")):
                    href: str = anchor_tag["href"]
                    text: str = anchor_tag.text

                    url_dict[year][text] = href

        return url_dict

    def _get_year_for_data(self, year_text: str) -> str:
        match = re.match(r"FY (\d{4})", year_text)

        if not match:
            raise Exception("this should have matched")

        return match.group(1)
