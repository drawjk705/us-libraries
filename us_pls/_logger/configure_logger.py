import logging
import sys

from us_pls._logger.filters import ModuleFilter

DEFAULT_LOG_FILE = "us-libraries.log"


def configure_logger(log_file: str, data_year: int) -> None:
    """
    sets up logger for the project

    Args:
        log_file (str): the name of the file that log output will be sent to
    """

    log_format = (
        "[PLS_{0} %(levelname)s] %(asctime)s [%(name)s:%(lineno)d] %(message)s".format(
            data_year
        )
    )
    date_format = "%Y-%m-%d %H:%M:%S%z"

    logger = logging.getLogger("us-libraries")
    logger.setLevel(logging.NOTSET)

    info_stream_handler = logging.StreamHandler(sys.stdout)
    info_stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(log_format, datefmt=date_format)
    info_stream_handler.setFormatter(formatter)
    info_stream_handler.addFilter(ModuleFilter())
    logger.addHandler(info_stream_handler)

    error_stream_handler = logging.StreamHandler(sys.stdout)
    error_stream_handler.setLevel(logging.ERROR)
    error_stream_handler.setFormatter(formatter)
    logger.addHandler(error_stream_handler)

    root_file_handler = logging.FileHandler(log_file)
    root_file_handler.setLevel(logging.NOTSET)
    root_file_handler.addFilter(ModuleFilter())
    root_file_handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        handlers=[root_file_handler, info_stream_handler],
    )
