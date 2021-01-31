# pyright: reportUnknownMemberType=false

import logging
import zipfile
from pathlib import Path
from typing import Dict

import requests

from us_pls._config import Config
from us_pls._download.interface import IDownloadService
from us_pls._download.models import DatafileType, DownloadType
from us_pls._logger.interface import ILoggerFactory
from us_pls._persistence.interface import IOnDiskCache
from us_pls._scraper.interface import IScrapingService

BASE_URL = "https://www.imls.gov"


class DownloadService(IDownloadService):
    _config: Config
    _scraper: IScrapingService
    _cache: IOnDiskCache
    _logger: logging.Logger

    def __init__(
        self,
        config: Config,
        scraper: IScrapingService,
        cache: IOnDiskCache,
        logger_factory: ILoggerFactory,
    ) -> None:
        self._config = config
        self._scraper = scraper
        self._cache = cache
        self._logger = logger_factory.get_logger(__name__)

    def download(self) -> None:
        scraped_dict = self._scraper.scrape_files()

        scraped_dict_for_year = scraped_dict.get(str(self._config.year))

        if scraped_dict_for_year is None:
            self._logger.info(f"There is no data for {self._config.year}")
            return

        self._try_download_resource(
            scraped_dict_for_year, "Documentation", DownloadType.Documentation
        )

        self._try_download_resource(scraped_dict_for_year, "CSV", DownloadType.CsvZip)

        self._try_download_resource(
            scraped_dict_for_year,
            "Data Element Definitions",
            DownloadType.DataElementDefinitions,
        )

        self._clean_up_readme()

    def _try_download_resource(
        self, scraped_dict: Dict[str, str], resource: str, download_type: DownloadType
    ) -> None:
        route = scraped_dict.get(resource)

        self._logger.debug(f"Trying to download {resource}")

        if route is None:
            self._logger.warning(
                f"The resource `{resource}` does not exist for {self._config.year}"
            )
            return

        if self._resource_already_exists(download_type):
            self._logger.debug(
                f"Resources have already been downloaded for {download_type.value}"
            )
            return

        url = f"{BASE_URL}/{route[1:] if route.startswith('/') else route}"

        res = requests.get(url)

        if res.status_code != 200:
            msg = f"Received a non-200 status code for {url}: {res.status_code}"

            self._logger.warning(msg)

            return

        self._write_content(
            download_type,
            res.content,
            should_unzip=str(download_type.value).endswith(".zip"),
        )

    def _resource_already_exists(self, download_type: DownloadType) -> bool:
        if download_type in [
            DownloadType.Documentation,
            DownloadType.DataElementDefinitions,
        ]:
            return self._cache.exists(download_type.value)
        elif download_type == DownloadType.CsvZip:
            return all(
                [
                    self._cache.exists(str(datafile_type.value))
                    for datafile_type in DatafileType
                ]
            )

        return False

    def _write_content(
        self, download_type: DownloadType, content: bytes, should_unzip: bool = False
    ) -> None:
        self._cache.put(content, download_type.value)

        if should_unzip:
            zip_path = self._cache.cache_path / Path(download_type.value)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self._cache.cache_path)

            self._move_content()
            self._cache.remove(zip_path)

    def _move_content(self) -> None:
        for path in self._cache.cache_path.iterdir():
            if not path.is_dir():
                self._rename(path)
                continue

            for sub_path in path.iterdir():
                self._rename(sub_path)
            self._cache.remove(path)

    def _rename(self, path: Path) -> None:
        new_name: str = path.name
        if "_ae_" in path.name.lower() or "ld" in path.name.lower():
            new_name = DatafileType.SystemData.value
        elif "_outlet_" in path.name.lower() or "out" in path.name.lower():
            new_name = DatafileType.OutletData.value
        elif "_state_" in path.name.lower() or "sum" in path.name.lower():
            new_name = DatafileType.SummaryData.value
        elif "readme" in path.name.lower():
            new_name = "README.txt"

        self._cache.rename(path, Path(new_name))

    def _clean_up_readme(self):
        self._logger.debug("Cleaning up readme")

        readme_text = self._cache.get(
            "README.txt",
            "txt",
            encoding="utf-8",
            errors="surrogateescape",
        )

        if readme_text is None:
            self._logger.debug("No readme exists for this year")
            return

        cleaned_readme_text = "".join([c if ord(c) < 128 else "'" for c in readme_text])

        self._cache.put(
            bytes(cleaned_readme_text, "utf-8"),
            "README.txt",
        )
