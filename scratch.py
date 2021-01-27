# pyright: reportUnknownMemberType=false
from us_libraries._logger.interface import ILoggerFactory
from us_libraries._logger.factory import LoggerFactory
from us_libraries._scraper.scraping_service import ScrapingService
from us_libraries._scraper.interface import IScrapingService
from us_libraries._download.download_service import DownloadService
import punq
from us_libraries._download.interface import IDownloadService
from us_libraries._config import Config

config = Config(2017)


container = punq.Container()

container.register(Config, instance=config)
container.register(ILoggerFactory, LoggerFactory)
container.register(IDownloadService, DownloadService)
container.register(IScrapingService, ScrapingService)


svc: DownloadService = container.resolve(IDownloadService)

svc.download()