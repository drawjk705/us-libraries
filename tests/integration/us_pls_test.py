import json
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Generator, List, cast
from unittest.mock import MagicMock

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
from us_pls._variables.models import Variables
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
                "https://www.imls.gov/sites/default/files/fy2017_pls_data_file_documentation.pdf",
                "https://www.imls.gov/sites/default/files/pls_fy2017_data_files_csv.zip",
            ]
    else:
        if downloaded_files_exist:
            assert api_calls == [
                "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
            ]
        else:
            assert api_calls == [
                "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey",
                "https://www.imls.gov/sites/default/files/fy2017_pls_data_file_documentation.pdf",
                "https://www.imls.gov/sites/default/files/pls_fy2017_data_files_csv.zip",
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
    mock_logger = MagicMock()

    mocker.patch.object(logging, "getLogger", return_value=mock_logger)

    try:
        PublicLibrariesSurvey(2017)
    except:
        pass

    cast(logging.Logger, mock_logger).warning.assert_called_with(
        "Received a non-200 status code for https://www.imls.gov/sites/default/files/fy2017_pls_data_file_documentation.pdf: 400"
    )


@pytest.mark.integration
@pytest.mark.parametrize(
    "datafile_type, expected_columns",
    [
        (
            DatafileType.OutletData,
            EXPECTED_OUTLET_DATA_COLS,
        ),
        (
            DatafileType.SummaryData,
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
            DatafileType.SummaryData,
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
def test_get_variables():
    lib = PublicLibrariesSurvey(2017)

    assert lib.summary_data_vars == Variables.from_dict(
        {
            "Identification": {"Name": "Identification_Name"},
            "Population": {
                "Of": {
                    "LegalServiceArea": "Population_Of_LegalServiceArea",
                    "F_POPLSA": "F_POPLSA",
                    "LegalServiceAreas_Unduplicated": "Population_Of_LegalServiceAreas_Unduplicated",
                    "State_EstimateTotal": "Population_Of_State_EstimateTotal",
                }
            },
            "ServiceOutlets": {
                "CountOf": {
                    "CentralLibraries": "ServiceOutlets_CountOf_CentralLibraries",
                    "F_CENLIB": "F_CENLIB",
                    "BranchLibraries": "ServiceOutlets_CountOf_BranchLibraries",
                    "F_BRLIB": "F_BRLIB",
                    "Bookmobiles": "ServiceOutlets_CountOf_Bookmobiles",
                    "F_BKMOB": "F_BKMOB",
                }
            },
            "FullTimePaidStaff": {
                "Librarians_WithMasters": "FullTimePaidStaff_Librarians_WithMasters",
                "F_MASTER": "F_MASTER",
                "Librarians": "FullTimePaidStaff_Librarians",
                "F_LIBRAR": "F_LIBRAR",
                "Other": "FullTimePaidStaff_Other",
                "F_OTHSTF": "F_OTHSTF",
                "Total": "FullTimePaidStaff_Total",
                "F_TOTSTF": "F_TOTSTF",
            },
            "OperatingRevenue": {
                "From": {
                    "LocalGovernment": "OperatingRevenue_From_LocalGovernment",
                    "F_LOCGVT": "F_LOCGVT",
                    "State": "OperatingRevenue_From_State",
                    "F_STGVT": "F_STGVT",
                    "FederalGovernment": "OperatingRevenue_From_FederalGovernment",
                    "F_FEDGVT": "F_FEDGVT",
                    "Other": "OperatingRevenue_From_Other",
                    "F_OTHINC": "F_OTHINC",
                    "Total": "OperatingRevenue_From_Total",
                    "F_TOTINC": "F_TOTINC",
                }
            },
            "OperatingExpenditures": {
                "Staff": {
                    "Salaries": "OperatingExpenditures_Staff_Salaries",
                    "F_SALX": "F_SALX",
                    "EmployeeBenefits": "OperatingExpenditures_Staff_EmployeeBenefits",
                    "F_BENX": "F_BENX",
                    "Total": "OperatingExpenditures_Staff_Total",
                    "F_TOSTFX": "F_TOSTFX",
                },
                "Collections": {
                    "Of": {
                        "PrintMaterials": "OperatingExpenditures_Collections_Of_PrintMaterials",
                        "F_PRMATX": "F_PRMATX",
                        "ElectonicMaterials": "OperatingExpenditures_Collections_Of_ElectonicMaterials",
                        "F_ELMATX": "F_ELMATX",
                        "OtherMaterials": "OperatingExpenditures_Collections_Of_OtherMaterials",
                        "F_OTMATX": "F_OTMATX",
                        "Total": "OperatingExpenditures_Collections_Of_Total",
                        "F_TOCOLX": "F_TOCOLX",
                    }
                },
                "Other": "OperatingExpenditures_Other",
                "F_OTHOPX": "F_OTHOPX",
                "Total": "OperatingExpenditures_Total",
                "F_TOTOPX": "F_TOTOPX",
            },
            "CapitalRevenue": {
                "From": {
                    "LocalGovernment": "CapitalRevenue_From_LocalGovernment",
                    "F_LCAPRV": "F_LCAPRV",
                    "State": "CapitalRevenue_From_State",
                    "F_SCAPRV": "F_SCAPRV",
                    "FederalGovernment": "CapitalRevenue_From_FederalGovernment",
                    "F_FCAPRV": "F_FCAPRV",
                    "Other": "CapitalRevenue_From_Other",
                    "F_OCAPRV": "F_OCAPRV",
                    "Total": "CapitalRevenue_From_Total",
                    "F_TCAPRV": "F_TCAPRV",
                }
            },
            "CapitalExpenditures": {
                "Total": "CapitalExpenditures_Total",
                "F_TCAPX": "F_TCAPX",
            },
            "LibraryCollections": {
                "CountOf": {
                    "PrintMaterials": "LibraryCollections_CountOf_PrintMaterials",
                    "F_BKVOL": "F_BKVOL",
                    "EBooks": "LibraryCollections_CountOf_EBooks",
                    "F_EBOOK": "F_EBOOK",
                    "Audio_Physical": "LibraryCollections_CountOf_Audio_Physical",
                    "F_AUD_PH": "F_AUD_PH",
                    "Audio_Downloadable": "LibraryCollections_CountOf_Audio_Downloadable",
                    "F_AUD_DL": "F_AUD_DL",
                    "Video_Physical": "LibraryCollections_CountOf_Video_Physical",
                    "F_VID_PH": "F_VID_PH",
                    "Video_Downloadable": "LibraryCollections_CountOf_Video_Downloadable",
                    "F_VID_DL": "F_VID_DL",
                }
            },
            "ElectronicCollections": {
                "From": {
                    "LocalOrOther": "ElectronicCollections_From_LocalOrOther",
                    "F_EC_L_O": "F_EC_L_O",
                    "State": "ElectronicCollections_From_State",
                    "F_EC_ST": "F_EC_ST",
                },
                "Total": "ElectronicCollections_Total",
                "F_ELECOL": "F_ELECOL",
            },
            "OtherCollections": {
                "CurrentPrintSerialSubscriptions": "OtherCollections_CurrentPrintSerialSubscriptions",
                "F_PRSUB": "F_PRSUB",
            },
            "Hours": {"Total": "Hours_Total", "F_HRS_OP": "F_HRS_OP"},
            "LibraryServices": {
                "Visits": "LibraryServices_Visits",
                "F_VISITS": "F_VISITS",
                "ReferenceTransactions": "LibraryServices_ReferenceTransactions",
                "F_REFER": "F_REFER",
                "RegisteredUsers": "LibraryServices_RegisteredUsers",
                "F_REGBOR": "F_REGBOR",
            },
            "Circulation": {
                "For": {
                    "ChildrenMaterials": "Circulation_For_ChildrenMaterials",
                    "F_KIDCIR": "F_KIDCIR",
                    "ElectronicMaterials": "Circulation_For_ElectronicMaterials",
                    "F_EMTCIR": "F_EMTCIR",
                    "PhysicalItems": "Circulation_For_PhysicalItems",
                    "F_PHYSCR": "F_PHYSCR",
                    "ElectronicInfo_SuccessfulRetrieval": "Circulation_For_ElectronicInfo_SuccessfulRetrieval",
                    "F_ELINFO": "F_ELINFO",
                    "ElectronicContentUse": "Circulation_For_ElectronicContentUse",
                    "F_ELCONT": "F_ELCONT",
                },
                "Total_Transactions": "Circulation_Total_Transactions",
                "F_TOTCIR": "F_TOTCIR",
                "Total_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval": "Circulation_Total_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval",
                "F_TOTCOL": "F_TOTCOL",
            },
            "InterLibraryLoans": {
                "Amount": {
                    "Given": "InterLibraryLoans_Amount_Given",
                    "F_LOANTO": "F_LOANTO",
                    "Received": "InterLibraryLoans_Amount_Received",
                    "F_LOANFM": "F_LOANFM",
                }
            },
            "LibraryPrograms": {
                "For": {
                    "Children": "LibraryPrograms_For_Children",
                    "F_KIDPRO": "F_KIDPRO",
                    "YoungAdults": "LibraryPrograms_For_YoungAdults",
                    "F_YAPRO": "F_YAPRO",
                },
                "Total": "LibraryPrograms_Total",
                "F_TOTPRO": "F_TOTPRO",
                "Attendance": {
                    "Total": "LibraryPrograms_Attendance_Total",
                    "F_TOTATT": "F_TOTATT",
                    "For": {
                        "Children": "LibraryPrograms_Attendance_For_Children",
                        "F_KIDATT": "F_KIDATT",
                        "YoungAdults": "LibraryPrograms_Attendance_For_YoungAdults",
                        "F_YAATT": "F_YAATT",
                    },
                },
            },
            "OtherElectronicInfo": {
                "CountOf": {
                    "Computers": "OtherElectronicInfo_CountOf_Computers",
                    "F_GPTERM": "F_GPTERM",
                    "ComputerUses": "OtherElectronicInfo_CountOf_ComputerUses",
                    "F_PITUSR": "F_PITUSR",
                    "WiFiSessions": "OtherElectronicInfo_CountOf_WiFiSessions",
                    "F_WIFISS": "F_WIFISS",
                    "VisitsToLibraryWebsite": "OtherElectronicInfo_CountOf_VisitsToLibraryWebsite",
                }
            },
            "Other": {
                "ReportingPeriod": {
                    "StartDate": "Other_ReportingPeriod_StartDate",
                    "EndDate": "Other_ReportingPeriod_EndDate",
                },
                "International CommitteeForInformationTechnologyStandardsStateCode_2Digit": "Other_International CommitteeForInformationTechnologyStandardsStateCode_2Digit",
                "SubmissionYearOfPublicLibraryData": "Other_SubmissionYearOfPublicLibraryData",
                "BureauOfEconomicsAnalysisCode": "Other_BureauOfEconomicsAnalysisCode",
            },
        }
    )
    assert lib.system_data_vars == Variables.from_dict(
        {
            "Identification": {
                "State": "Identification_State",
                "Name": "Identification_Name",
                "LibraryIdCode": {
                    "FromIMLS": "Identification_LibraryIdCode_FromIMLS",
                    "FromState": "Identification_LibraryIdCode_FromState",
                },
            },
            "StreetAddress": {
                "Address": "StreetAddress_Address",
                "City": "StreetAddress_City",
                "ZipCode": "StreetAddress_ZipCode",
                "ZipCode_4Digit": "StreetAddress_ZipCode_4Digit",
            },
            "MailingAggress": {
                "Address": "MailingAggress_Address",
                "City": "MailingAggress_City",
                "ZipCode": "MailingAggress_ZipCode",
                "ZipCode_4Digit": "MailingAggress_ZipCode_4Digit",
                "County": "MailingAggress_County",
                "PhoneNumber": "MailingAggress_PhoneNumber",
            },
            "InterlibraryRelationshipCode": "InterlibraryRelationshipCode",
            "LegalBasisCode": "LegalBasisCode",
            "AdministrativeStructureCode": "AdministrativeStructureCode",
            "MeetsDefinitionOfPublicLibrary": "MeetsDefinitionOfPublicLibrary",
            "TypeOfRegionServed": "TypeOfRegionServed",
            "DidLegalServiceAreaChanceInPastYear": "DidLegalServiceAreaChanceInPastYear",
            "ReportingPeriodStartDate": "ReportingPeriodStartDate",
            "ReportingPeriodEndDate": "ReportingPeriodEndDate",
            "Population": {
                "Of": {
                    "LegalServiceArea": "Population_Of_LegalServiceArea",
                    "F_POPLSA": "F_POPLSA",
                    "LegalServiceArea_Unduplicated": "Population_Of_LegalServiceArea_Unduplicated",
                }
            },
            "ServiceOutlets": {
                "CountOf": {
                    "CentralLibraries": "ServiceOutlets_CountOf_CentralLibraries",
                    "F_CENLIB": "F_CENLIB",
                    "BranchLibraries": "ServiceOutlets_CountOf_BranchLibraries",
                    "F_BRLIB": "F_BRLIB",
                    "Bookmobiles": "ServiceOutlets_CountOf_Bookmobiles",
                    "F_BKMOB": "F_BKMOB",
                }
            },
            "FullTimePaidStaff": {
                "CountOf": {
                    "PaidLibrarians_WithMasters": "FullTimePaidStaff_CountOf_PaidLibrarians_WithMasters",
                    "F_MASTER": "F_MASTER",
                    "Employees_WithTitleLibrarian": "FullTimePaidStaff_CountOf_Employees_WithTitleLibrarian",
                    "F_LIBRAR": "F_LIBRAR",
                    "OtherPaidStaff": "FullTimePaidStaff_CountOf_OtherPaidStaff",
                    "F_OTHSTF": "F_OTHSTF",
                },
                "Total": "FullTimePaidStaff_Total",
                "F_TOTSTF": "F_TOTSTF",
            },
            "OperatingRevenue": {
                "From": {
                    "LocalGovernment": "OperatingRevenue_From_LocalGovernment",
                    "F_LOCGVT": "F_LOCGVT",
                    "StateGovernment": "OperatingRevenue_From_StateGovernment",
                    "F_STGVT": "F_STGVT",
                    "FederalGovernment": "OperatingRevenue_From_FederalGovernment",
                    "F_FEDGVT": "F_FEDGVT",
                    "OtherSources": "OperatingRevenue_From_OtherSources",
                    "F_OTHINC": "F_OTHINC",
                },
                "Total": "OperatingRevenue_Total",
                "F_TOTINC": "F_TOTINC",
            },
            "OperatingExpenditures": {
                "Staff": {
                    "Wages": "OperatingExpenditures_Staff_Wages",
                    "F_SALX": "F_SALX",
                    "EmployeeBenefits": "OperatingExpenditures_Staff_EmployeeBenefits",
                    "F_BENX": "F_BENX",
                    "Total": "OperatingExpenditures_Staff_Total",
                    "F_TOSTFX": "F_TOSTFX",
                },
                "Collection": {
                    "PrintMaterials": "OperatingExpenditures_Collection_PrintMaterials",
                    "F_PRMATX": "F_PRMATX",
                    "ElectronicMaterials": "OperatingExpenditures_Collection_ElectronicMaterials",
                    "F_ELMATX": "F_ELMATX",
                    "OtherMaterials": "OperatingExpenditures_Collection_OtherMaterials",
                    "F_OTMATX": "F_OTMATX",
                    "Total": "OperatingExpenditures_Collection_Total",
                    "F_TOCOLX": "F_TOCOLX",
                },
                "Other": "OperatingExpenditures_Other",
                "F_OTHOPX": "F_OTHOPX",
                "Total": "OperatingExpenditures_Total",
                "F_TOTOPX": "F_TOTOPX",
            },
            "CapitalRevenue": {
                "From": {
                    "LocalGovernment": "CapitalRevenue_From_LocalGovernment",
                    "F_LCAPRV": "F_LCAPRV",
                    "StateGovernment": "CapitalRevenue_From_StateGovernment",
                    "F_SCAPRV": "F_SCAPRV",
                    "FederalGovernment": "CapitalRevenue_From_FederalGovernment",
                    "F_FCAPRV": "F_FCAPRV",
                    "Other": "CapitalRevenue_From_Other",
                    "F_OCAPRV": "F_OCAPRV",
                    "Total": "CapitalRevenue_From_Total",
                    "F_TCAPRV": "F_TCAPRV",
                }
            },
            "CapitalExpenditures": {
                "Total": "CapitalExpenditures_Total",
                "F_TCAPX": "F_TCAPX",
            },
            "LibraryCollection": {
                "CountOf": {
                    "PrintMaterials": "LibraryCollection_CountOf_PrintMaterials",
                    "F_BKVOL": "F_BKVOL",
                    "ElectronicMaterials": "LibraryCollection_CountOf_ElectronicMaterials",
                    "F_EBOOK": "F_EBOOK",
                    "AudioMaterials_Physical": "LibraryCollection_CountOf_AudioMaterials_Physical",
                    "F_AUD_PH": "F_AUD_PH",
                    "AudioMaterials_Downloadable": "LibraryCollection_CountOf_AudioMaterials_Downloadable",
                    "F_AUD_DL": "F_AUD_DL",
                    "VideoMaterials_Physical": "LibraryCollection_CountOf_VideoMaterials_Physical",
                    "F_VID_PH": "F_VID_PH",
                    "VideoMaterials_Downloadable": "LibraryCollection_CountOf_VideoMaterials_Downloadable",
                    "F_VID_DL": "F_VID_DL",
                }
            },
            "ElectronicCollection": {
                "From": {
                    "LocalOrOther": "ElectronicCollection_From_LocalOrOther",
                    "F_EC_L_O": "F_EC_L_O",
                    "State": "ElectronicCollection_From_State",
                    "F_EC_ST": "F_EC_ST",
                },
                "Total": "ElectronicCollection_Total",
                "F_ELECOL": "F_ELECOL",
            },
            "PrintSerialSubscriptions": {
                "Total": "PrintSerialSubscriptions_Total",
                "F_PRSUB": "F_PRSUB",
            },
            "PublicServiceHours": {
                "Total_PerYear": "PublicServiceHours_Total_PerYear",
                "F_HRS_OP": "F_HRS_OP",
            },
            "LibraryServices": {
                "CountOf": {
                    "Visits": "LibraryServices_CountOf_Visits",
                    "F_VISITS": "F_VISITS",
                    "ReferenceTransactions": "LibraryServices_CountOf_ReferenceTransactions",
                    "F_REFER": "F_REFER",
                    "RegisteredUsers": "LibraryServices_CountOf_RegisteredUsers",
                    "F_REGBOR": "F_REGBOR",
                }
            },
            "Circulation": {
                "CountOf": {
                    "Transactions": "Circulation_CountOf_Transactions",
                    "F_TOTCIR": "F_TOTCIR",
                    "OfChildrenMaterials": "Circulation_CountOf_OfChildrenMaterials",
                    "F_KIDCIR": "F_KIDCIR",
                    "OfElectronicMaterials": "Circulation_CountOf_OfElectronicMaterials",
                    "F_EMTCIR": "F_EMTCIR",
                    "OfPhysicalMaterials": "Circulation_CountOf_OfPhysicalMaterials",
                    "F_PHYSCR": "F_PHYSCR",
                    "SuccessfulRetrievalOfElectronicInfo": "Circulation_CountOf_SuccessfulRetrievalOfElectronicInfo",
                    "F_ELINFO": "F_ELINFO",
                    "ElectronicContentUse": "Circulation_CountOf_ElectronicContentUse",
                    "F_ELCONT": "F_ELCONT",
                },
                "Total": "Circulation_Total",
                "F_TOTCOL": "F_TOTCOL",
            },
            "InterLibraryLoans": {
                "Amount": {
                    "Given": "InterLibraryLoans_Amount_Given",
                    "F_LOANTO": "F_LOANTO",
                    "Received": "InterLibraryLoans_Amount_Received",
                    "F_LOANFM": "F_LOANFM",
                }
            },
            "LibraryPrograms": {
                "CountOf": {
                    "ForChildren": "LibraryPrograms_CountOf_ForChildren",
                    "F_KIDPRO": "F_KIDPRO",
                    "ForYoungAdults": "LibraryPrograms_CountOf_ForYoungAdults",
                    "F_YAPRO": "F_YAPRO",
                },
                "Total": "LibraryPrograms_Total",
                "F_TOTPRO": "F_TOTPRO",
                "Attendance": {
                    "Total": "LibraryPrograms_Attendance_Total",
                    "F_TOTATT": "F_TOTATT",
                    "ForChildren": "LibraryPrograms_Attendance_ForChildren",
                    "F_KIDATT": "F_KIDATT",
                    "ForYoungAdults": "LibraryPrograms_Attendance_ForYoungAdults",
                    "F_YAATT": "F_YAATT",
                },
            },
            "OtherElectronicInformation": {
                "CountOf": {
                    "ComputersUsedByPublic": "OtherElectronicInformation_CountOf_ComputersUsedByPublic",
                    "F_GPTERM": "F_GPTERM",
                    "UsagesOfComputers": "OtherElectronicInformation_CountOf_UsagesOfComputers",
                    "F_PITUSR": "F_PITUSR",
                    "WiFiUses": "OtherElectronicInformation_CountOf_WiFiUses",
                    "F_WIFISS": "F_WIFISS",
                    "VisitsToLibraryWebsite": "OtherElectronicInformation_CountOf_VisitsToLibraryWebsite",
                }
            },
            "Other": {
                "ReportingPeriod": {
                    "StartDate": "Other_ReportingPeriod_StartDate",
                    "EndDate": "Other_ReportingPeriod_EndDate",
                },
                "SubmissionYearOfPublicLibraryData": "Other_SubmissionYearOfPublicLibraryData",
                "BureauOfEconomicAnalysisCode": "Other_BureauOfEconomicAnalysisCode",
                "ReportingStatus": "Other_ReportingStatus",
                "StructureChangeCode": "Other_StructureChangeCode",
                "NameChangeCode": "Other_NameChangeCode",
                "AddressChangeCode": "Other_AddressChangeCode",
                "Longitute": "Other_Longitute",
                "Latitude": "Other_Latitude",
                "InternationalCommitteeForInfoTechStandardsStateCode_2Digit": "Other_InternationalCommitteeForInfoTechStandardsStateCode_2Digit",
                "InternationalCommitteeForInfoTechStandardsStateCode_3Digit": "Other_InternationalCommitteeForInfoTechStandardsStateCode_3Digit",
                "GeographicNamesInformationSystemFeatureId": "Other_GeographicNamesInformationSystemFeatureId",
                "CountyPopulation": "Other_CountyPopulation",
                "CateorizationOfLocale": {
                    "CategorizationBySizeAndProximityToCities": "Other_CateorizationOfLocale_CategorizationBySizeAndProximityToCities",
                    "CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets": "Other_CateorizationOfLocale_CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets",
                    "CategorizationBySizeAndProximityToCities_FromRuralEducationAchievementProgram": "Other_CateorizationOfLocale_CategorizationBySizeAndProximityToCities_FromRuralEducationAchievementProgram",
                    "CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets_FromRuralEducationAchievementProgram": "Other_CateorizationOfLocale_CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets_FromRuralEducationAchievementProgram",
                },
                "CensusTract": "Other_CensusTract",
                "CensusBlock": "Other_CensusBlock",
                "CongressionalDistrict": "Other_CongressionalDistrict",
                "CoreBasedStatisticalArea": "Other_CoreBasedStatisticalArea",
                "MetropolitanAndMicropolitcanStatisticalAreaFlag": "Other_MetropolitanAndMicropolitcanStatisticalAreaFlag",
                "Geocoding_AccuraryAndPrecision": "Other_Geocoding_AccuraryAndPrecision",
            },
        }
    )
    assert lib.outlet_data_vars == Variables.from_dict(
        {
            "Identification": {
                "State": "Identification_State",
                "LibraryIdCode": {
                    "FromIMLS": "Identification_LibraryIdCode_FromIMLS",
                    "Suffix": "Identification_LibraryIdCode_Suffix",
                    "FromState": "Identification_LibraryIdCode_FromState",
                },
                "MeetsDefinitionOfPublicLibrary": "Identification_MeetsDefinitionOfPublicLibrary",
                "Name": "Identification_Name",
                "Address": "Identification_Address",
                "City": "Identification_City",
                "ZipCode": "Identification_ZipCode",
                "ZipCode_4Digit": "Identification_ZipCode_4Digit",
                "County": "Identification_County",
                "Phone": "Identification_Phone",
            },
            "OutletType": "OutletType",
            "SquareFootage": "SquareFootage",
            "F_SQ_FT": "F_SQ_FT",
            "Num_BookmobilesInBookmobileOutletRecord": "Num_BookmobilesInBookmobileOutletRecord",
            "HoursOpen": "HoursOpen",
            "WeeksOpen": "WeeksOpen",
            "SubmissionYearOfPublicLibraryData": "SubmissionYearOfPublicLibraryData",
            "BureauOfEconomicsAnalysisCode": "BureauOfEconomicsAnalysisCode",
            "StructureChangeCode": "StructureChangeCode",
            "NameChangeCode": "NameChangeCode",
            "AddressChangeCode": "AddressChangeCode",
            "Longitude": "Longitude",
            "Latitude": "Latitude",
            "InternationalCommiteeForInfoTechStandardsStateCode_TwoDigit": "InternationalCommiteeForInfoTechStandardsStateCode_TwoDigit",
            "InternationalCommiteeForInfoTechStandardsStateCode_ThreeDigit": "InternationalCommiteeForInfoTechStandardsStateCode_ThreeDigit",
            "GeographicNamesInformationSystemFeatureId": "GeographicNamesInformationSystemFeatureId",
            "CountyPopulation": "CountyPopulation",
            "CategorizationOfLocale": {
                "BySizeAndProximityToCities": "CategorizationOfLocale_BySizeAndProximityToCities",
                "BySizeAndProximityToCities_FromRuralEducationAchievementProgram": "CategorizationOfLocale_BySizeAndProximityToCities_FromRuralEducationAchievementProgram",
            },
            "CensusTract": "CensusTract",
            "CensusBlock": "CensusBlock",
            "CongressionalDistrict": "CongressionalDistrict",
            "CoreBasedStatisticalArea": "CoreBasedStatisticalArea",
            "MetropolitanAndMicropolitcanStatisticalAreaFlag": "MetropolitanAndMicropolitcanStatisticalAreaFlag",
            "Geocoding_AccuracyAndPrecision": "Geocoding_AccuracyAndPrecision",
        }
    )


@pytest.mark.integration
def test_repr():
    lib = PublicLibrariesSurvey(2017)

    assert str(lib) == "<PublicLibrariesSurvey 2017>"
