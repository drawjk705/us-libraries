import json
import os
import shutil
from pathlib import Path
from typing import Any, Generator, List

import pytest
import requests
from _pytest.capture import CaptureFixture
from pytest_mock.plugin import MockerFixture

from tests.integration.expected_stat_columns import (
    EXPECTED_OUTLET_DATA_COLS,
    EXPECTED_STATE_SUM_COLS,
    EXPECTED_SYS_DATA_COLS,
)
from tests.utils import MockRes, shuffled_cases
from us_pls._download.models import DatafileType
from us_pls.libraries import PublicLibrariesSurvey


@pytest.fixture(autouse=True)
def api_calls(mocker: MockerFixture) -> List[str]:
    calls = []

    def requests_handler(route: str, *args: Any, **kwargs: Any):
        calls.append(route)

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
                return MockRes(400)

    mocker.patch.object(requests, "get", requests_handler)

    return calls


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


def given_downloaded_files_exist():
    datapath = Path("data/2017")

    datapath.mkdir(parents=True, exist_ok=True)

    with open(f"{datapath}/Documentation.pdf", "wb"):
        pass

    with open(f"{datapath}/README.txt", "w"):
        pass

    with open(f"{datapath}/OutletData.csv", "w"):
        pass

    with open(f"{datapath}/StateSummaryAndCharacteristicData.csv", "w"):
        pass

    with open(f"{datapath}/SystemData.csv", "w"):
        pass


def given_urls_file_exists():
    path = Path("data")

    path.mkdir(parents=True, exist_ok=True)

    with open(f"{path}/urls.json", "w") as f:
        json.dump(
            {
                "2017": {
                    "CSV": "/sites/default/files/pls_fy2017_data_files_csv.zip",
                    "SAS": "/sites/default/files/pls_fy2017_data_files_sas.zip",
                    "SPSS": "/sites/default/files/pls_fy2017_data_files_spss.zip",
                    "Documentation": "/sites/default/files/fy2017_pls_data_file_documentation.pdf",
                    "Volume 1": "/publications/public-libraries-united-states-survey-fiscal-year-2017-volume-1",
                    "Volume 2": "/publications/public-libraries-united-states-survey-fiscal-year-2017-volume-2",
                    "Rural Libraries in America: An Infographic Overview": "/publications/rural-libraries-america-infographic-overview",
                    "XLSX": "/sites/default/files/rural_libraries_in_america_state_detail_tables_worksheet_20200915.xlsx",
                    "PDF": "/sites/default/files/rural_libraries_in_america_state_detail_tables_20200915.pdf",
                    "Supplementary Tables": "/sites/default/files/fy2017_pls_tables.pdf",
                    "State Profiles": "/data/data-catalog/public-libraries-survey/fy-2017-pls-state-profiles",
                    "News Release": "/news/over-118-million-people-attended-library-programs-annually",
                },
            },
            f,
        )


data_files = [
    "data/2017/Documentation.pdf",
    "data/2017/SystemData.csv",
    "data/2017/StateSummaryAndCharacteristicData.csv",
    "data/2017/README.txt",
    "data/2017/OutletData.csv",
]


@pytest.mark.integration
def test_init_if_no_files_exist_downloads_datafiles(mocker: MockerFixture):
    for data_file in data_files:
        assert not Path(data_file).exists()

    _ = PublicLibrariesSurvey(
        2017,
        should_overwrite_cached_urls=False,
        should_overwrite_existing_cache=False,
    )

    for data_file in data_files:
        assert Path(data_file).exists()


@pytest.mark.integration
@pytest.mark.parametrize(
    *shuffled_cases(
        urls_file_exists=[True, False], downloaded_files_exist=[True, False]
    )
)
def test_api_hits(
    api_calls: List[str], urls_file_exists: bool, downloaded_files_exist: bool
):
    if urls_file_exists:
        given_urls_file_exists()
    if downloaded_files_exist:
        given_downloaded_files_exist()

    _ = PublicLibrariesSurvey(
        2017,
        should_overwrite_cached_urls=False,
        should_overwrite_existing_cache=False,
    )

    if urls_file_exists:
        if downloaded_files_exist:
            assert api_calls == []
        else:
            assert api_calls == [
                "https://www.imls.gov//sites/default/files/fy2017_pls_data_file_documentation.pdf",
                "https://www.imls.gov//sites/default/files/pls_fy2017_data_files_csv.zip",
            ]
    else:
        if downloaded_files_exist:
            assert api_calls == [
                "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
            ]
        else:
            assert api_calls == [
                "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey",
                "https://www.imls.gov//sites/default/files/fy2017_pls_data_file_documentation.pdf",
                "https://www.imls.gov//sites/default/files/pls_fy2017_data_files_csv.zip",
            ]


@pytest.mark.integration
def test_given_scraper_returns_400(mocker: MockerFixture):
    mocker.patch.object(requests, "get", return_value=MockRes(400))

    with pytest.raises(
        Exception,
        match="Got a non-200 status code for https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey: 400",
    ):
        PublicLibrariesSurvey(2017)


@pytest.mark.integration
def test_given_download_returns_400(mocker: MockerFixture):
    with open("../mock_api/mock_api_res.html", "r") as f:
        html = f.read()

    mocker.patch.object(
        requests, "get", side_effect=[MockRes(200, content=html), MockRes(400)]
    )

    with pytest.raises(
        Exception,
        match="Received a non-200 status code for https://www.imls.gov//sites/default/files/fy2017_pls_data_file_documentation.pdf: 400",
    ):
        PublicLibrariesSurvey(2017)


@pytest.mark.integration
@pytest.mark.parametrize(
    "datafile_type, expected_columns",
    [
        (
            DatafileType.OutletData,
            EXPECTED_OUTLET_DATA_COLS,
        ),
        (
            DatafileType.StateSummaryAndCharacteristicData,
            EXPECTED_STATE_SUM_COLS,
        ),
        (
            DatafileType.SystemData,
            EXPECTED_SYS_DATA_COLS,
        ),
    ],
)
def test_stats(datafile_type: DatafileType, expected_columns: List[str]):
    lib = PublicLibrariesSurvey(2017)

    columns = lib.get_stats(datafile_type).columns.tolist()

    assert columns == expected_columns


@pytest.mark.integration
@pytest.mark.parametrize(
    "datafile_type, expected_value",
    [
        (
            DatafileType.OutletData,
            "Public Library Outlet Data File includes a total of 17,452 total records. The file includes identifying information and a few basic data items for public library service outlets (central, branch, bookmobile, and books-by-mail-only outlets). The data for each outlet consist of one record, except where a single outlet represents multiple bookmobiles. For these outlets, a single record includes information for all bookmobiles and the variable L_NUM_BM indicates the number of associated bookmobiles.  The file includes 96 records for outlets that were reported as closed or were temporarily closed for FY 2017 (STATSTRU, Structure Change Code, is '03' or '23'). Records for public libraries that were closed for the current year are included in the file for that year only. The closed records are not included in the appendix tables of the data documentation or the Supplementary Tables. Data for the closed records are set to a value of -3 (closed or temporarily closed outlet), with flag U_17.\n",
        ),
        (
            DatafileType.StateSummaryAndCharacteristicData,
            "Public Library State Summary/State Characteristics Data File includes one record (a total of 54 records are in the data file) for each state and outlying area. All libraries, including those that do not conform to the FSCS definition of a public library, are included in the aggregate counts on the State Summary/State Characteristics Data File. For this reason, the Public Library System Data File is the primary source for producing the publication tables because libraries that do not meet the FSCS definition can be excluded from the aggregations. The State Summary/State Characteristics file includes: \n    a. State summary data. These are the totals of the numeric data from the public-use Public Library System Data File for each state and outlying area. \n    b. State characteristics data. These data consist of four items reported by each state and outlying area in a 'state characteristics' record: (1) the earliest reporting period starting date and (2) the latest reporting period ending date for their public libraries, (3) the state population estimate, and (4) the total unduplicated population of legal service areas in the state.\n",
        ),
        (
            DatafileType.SystemData,
            "Public Library System Data File. This file, also known as the Administrative Entity or AE file, includes a total of 9,245 records. Each library's data consist of one record. The file includes 29 records for administrative entities that were reported as closed or were temporarily closed for FY 2017 (STATSTRU, Structure Change Code, is '03' or '23'). Records for public libraries that were closed for the current year are included in the file for that year only. The closed records are not included in the appendix tables of the data documentation or the Supplementary Tables. Data for the closed records are set to a value of -3 (closed or temporarily closed administrative entity), with flag U_17.\n",
        ),
    ],
)
def test_read_docs(
    capsys: CaptureFixture[str], datafile_type: DatafileType, expected_value: str
):
    lib = PublicLibrariesSurvey(2017)

    lib.read_docs(on=datafile_type)

    assert capsys.readouterr().out == expected_value


@pytest.mark.integration
def test_repr():
    lib = PublicLibrariesSurvey(2017)

    assert str(lib) == "<PublicLibrariesSurvey 2017>"
