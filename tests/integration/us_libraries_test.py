import os
import shutil
from pathlib import Path
from typing import Any, Generator, List

import pytest
import requests
import tabula
from pytest_mock.plugin import MockerFixture

from tests.utils import MockRes
from us_libraries.libraries import Libraries

api_calls: List[str] = []


@pytest.fixture(autouse=True)
def mock_api(mocker: MockerFixture):
    api_calls = []

    def requests_handler(route: str, *args: Any, **kwargs: Any):
        api_calls.append(route)

        if (
            route
            == "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
        ):
            with open("../mock_api/mock_api_res.html", "r") as f:
                return MockRes(200, f.read())
        else:
            if route.endswith("/sites/default/files/pls_fy2017_data_files_csv.zip"):
                with open("../mock_api/pls_fy2017_data_files_csv.zip", "rb") as f:
                    return MockRes(200, f.read())
            elif route.endswith(
                "/sites/default/files/fy2017_pls_data_file_documentation.pdf"
            ):
                with open(
                    "../mock_api/fy2017_pls_data_file_documentation.pdf", "rb"
                ) as f:
                    return MockRes(200, f.read())
            else:
                raise Exception(f"Unknown route {route}")

    mocker.patch.object(requests, "get", requests_handler)


@pytest.fixture(autouse=True)
def set_current_path() -> Generator[None, None, None]:
    parent_path = Path(__file__).parent.absolute()

    os.chdir(parent_path)

    temp_dir = Path("temp")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir(parents=True, exist_ok=False)

    os.chdir(temp_dir.absolute())

    try:
        yield

    finally:
        os.chdir(parent_path)
        shutil.rmtree(temp_dir.absolute())


data_files = [
    "data/2017/Documentation.pdf",
    "data/2017/SystemDataFile.csv",
    "data/2017/StateSummaryAndCharacteristicData.csv",
    "data/2017/README FY17 PLS PUD.txt",
    "data/2017/OutletData.csv",
]


@pytest.mark.integration
def test_init_given_data_has_not_been_parsed(mocker: MockerFixture):
    for data_file in data_files:
        assert not Path(data_file).exists()

    tabula_spy = mocker.spy(tabula, "read_pdf")

    _ = Libraries(
        2017,
        should_cache_on_disk=True,
        should_overwrite_cached_urls=False,
        should_overwrite_existing_cache=False,
    )

    assert len(tabula_spy.call_args_list) == 3

    for data_file in data_files:
        assert Path(data_file).exists()
