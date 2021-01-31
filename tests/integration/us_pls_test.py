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

    columns = sorted(lib.get_stats(datafile_type).columns.tolist())

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
            "Name": "Name",
            "Population": {
                "Of": {
                    "LegalServiceArea": "Population_Of_LegalServiceArea",
                    "LegalServiceArea_ImputationFlag": "Population_Of_LegalServiceArea_ImputationFlag",
                    "LegalServiceAreas_Unduplicated": "Population_Of_LegalServiceAreas_Unduplicated",
                    "State_EstimateTotal": "Population_Of_State_EstimateTotal",
                }
            },
            "ServiceOutlets": {
                "CountOf": {
                    "CentralLibraries": "ServiceOutlets_CountOf_CentralLibraries",
                    "CentralLibraries_ImputationFlag": "ServiceOutlets_CountOf_CentralLibraries_ImputationFlag",
                    "BranchLibraries": "ServiceOutlets_CountOf_BranchLibraries",
                    "BranchLibraries_ImputationFlag": "ServiceOutlets_CountOf_BranchLibraries_ImputationFlag",
                    "Bookmobiles": "ServiceOutlets_CountOf_Bookmobiles",
                    "Bookmobiles_ImputationFlag": "ServiceOutlets_CountOf_Bookmobiles_ImputationFlag",
                }
            },
            "FullTimePaidStaff": {
                "Librarians_WithMasters": "FullTimePaidStaff_Librarians_WithMasters",
                "Librarians_WithMasters_ImputationFlag": "FullTimePaidStaff_Librarians_WithMasters_ImputationFlag",
                "Librarians": "FullTimePaidStaff_Librarians",
                "Librarians_ImputationFlag": "FullTimePaidStaff_Librarians_ImputationFlag",
                "Other": "FullTimePaidStaff_Other",
                "Other_ImputationFlag": "FullTimePaidStaff_Other_ImputationFlag",
                "Total": "FullTimePaidStaff_Total",
                "Total_ImputationFlag": "FullTimePaidStaff_Total_ImputationFlag",
            },
            "OperatingRevenue": {
                "From": {
                    "LocalGovernment": "OperatingRevenue_From_LocalGovernment",
                    "LocalGovernment_ImputationFlag": "OperatingRevenue_From_LocalGovernment_ImputationFlag",
                    "StateGovernment": "OperatingRevenue_From_StateGovernment",
                    "StateGovernment_ImputationFlag": "OperatingRevenue_From_StateGovernment_ImputationFlag",
                    "FederalGovernment": "OperatingRevenue_From_FederalGovernment",
                    "FederalGovernment_ImputationFlag": "OperatingRevenue_From_FederalGovernment_ImputationFlag",
                    "Other": "OperatingRevenue_From_Other",
                    "Other_ImputationFlag": "OperatingRevenue_From_Other_ImputationFlag",
                },
                "Total": "OperatingRevenue_Total",
                "Total_ImputationFlag": "OperatingRevenue_Total_ImputationFlag",
            },
            "OperatingExpenditures": {
                "On": {
                    "Staff": {
                        "Salaries": "OperatingExpenditures_On_Staff_Salaries",
                        "Salaries_ImputationFlag": "OperatingExpenditures_On_Staff_Salaries_ImputationFlag",
                        "EmployeeBenefits": "OperatingExpenditures_On_Staff_EmployeeBenefits",
                        "EmployeeBenefits_ImputationFlag": "OperatingExpenditures_On_Staff_EmployeeBenefits_ImputationFlag",
                        "Total": "OperatingExpenditures_On_Staff_Total",
                        "Total_ImputationFlag": "OperatingExpenditures_On_Staff_Total_ImputationFlag",
                    },
                    "Collections": {
                        "Of": {
                            "PrintMaterials": "OperatingExpenditures_On_Collections_Of_PrintMaterials",
                            "PrintMaterials_ImputationFlag": "OperatingExpenditures_On_Collections_Of_PrintMaterials_ImputationFlag",
                            "ElectronicMaterials": "OperatingExpenditures_On_Collections_Of_ElectronicMaterials",
                            "ElectronicMaterials_ImputationFlag": "OperatingExpenditures_On_Collections_Of_ElectronicMaterials_ImputationFlag",
                            "OtherMaterials": "OperatingExpenditures_On_Collections_Of_OtherMaterials",
                            "OtherMaterials_ImputationFlag": "OperatingExpenditures_On_Collections_Of_OtherMaterials_ImputationFlag",
                            "Total": "OperatingExpenditures_On_Collections_Of_Total",
                            "Total_ImputationFlag": "OperatingExpenditures_On_Collections_Of_Total_ImputationFlag",
                        }
                    },
                    "Other": "OperatingExpenditures_On_Other",
                    "Other_ImputationFlag": "OperatingExpenditures_On_Other_ImputationFlag",
                },
                "Total": "OperatingExpenditures_Total",
                "Total_ImputationFlag": "OperatingExpenditures_Total_ImputationFlag",
            },
            "CapitalRevenue": {
                "From": {
                    "LocalGovernment": "CapitalRevenue_From_LocalGovernment",
                    "LocalGovernment_ImputationFlag": "CapitalRevenue_From_LocalGovernment_ImputationFlag",
                    "State": "CapitalRevenue_From_State",
                    "State_ImputationFlag": "CapitalRevenue_From_State_ImputationFlag",
                    "FederalGovernment": "CapitalRevenue_From_FederalGovernment",
                    "FederalGovernment_ImputationFlag": "CapitalRevenue_From_FederalGovernment_ImputationFlag",
                    "Other": "CapitalRevenue_From_Other",
                    "Other_ImputationFlag": "CapitalRevenue_From_Other_ImputationFlag",
                },
                "Total": "CapitalRevenue_Total",
                "Total_ImputationFlag": "CapitalRevenue_Total_ImputationFlag",
            },
            "CapitalExpenditures": {
                "Total": "CapitalExpenditures_Total",
                "Total_ImputationFlag": "CapitalExpenditures_Total_ImputationFlag",
            },
            "LibraryCollections": {
                "CountOf": {
                    "PrintMaterials": "LibraryCollections_CountOf_PrintMaterials",
                    "PrintMaterials_ImputationFlag": "LibraryCollections_CountOf_PrintMaterials_ImputationFlag",
                    "EBooks": "LibraryCollections_CountOf_EBooks",
                    "EBooks_ImputationFlag": "LibraryCollections_CountOf_EBooks_ImputationFlag",
                    "Audio_Physical": "LibraryCollections_CountOf_Audio_Physical",
                    "AudioPhysical_ImputationFlag": "LibraryCollections_CountOf_AudioPhysical_ImputationFlag",
                    "Audio_Downloadable": "LibraryCollections_CountOf_Audio_Downloadable",
                    "Audio_Downloadable_ImputationFlag": "LibraryCollections_CountOf_Audio_Downloadable_ImputationFlag",
                    "Video_Physical": "LibraryCollections_CountOf_Video_Physical",
                    "Video_Physical_ImputationFlag": "LibraryCollections_CountOf_Video_Physical_ImputationFlag",
                    "Video_Downloadable": "LibraryCollections_CountOf_Video_Downloadable",
                    "Video_Downloadable_ImputationFlag": "LibraryCollections_CountOf_Video_Downloadable_ImputationFlag",
                }
            },
            "ElectronicCollections": {
                "From": {
                    "LocalOrOther": "ElectronicCollections_From_LocalOrOther",
                    "Other_ImputationFlag": "ElectronicCollections_From_Other_ImputationFlag",
                    "State": "ElectronicCollections_From_State",
                    "State_ImputationFlag": "ElectronicCollections_From_State_ImputationFlag",
                },
                "Total": "ElectronicCollections_Total",
                "Total_ImputationFlag": "ElectronicCollections_Total_ImputationFlag",
            },
            "OtherCollections": {
                "CurrentPrintSerialSubscriptions": "OtherCollections_CurrentPrintSerialSubscriptions",
                "CurrentPrintSerialSubscriptions_ImputationFlag": "OtherCollections_CurrentPrintSerialSubscriptions_ImputationFlag",
            },
            "Hours": {
                "Total": "Hours_Total",
                "Total_ImputationFlag": "Hours_Total_ImputationFlag",
            },
            "LibraryServices": {
                "CountOf": {
                    "Visits": "LibraryServices_CountOf_Visits",
                    "Visits_ImputationFlag": "LibraryServices_CountOf_Visits_ImputationFlag",
                    "ReferenceTransactions": "LibraryServices_CountOf_ReferenceTransactions",
                    "ReferenceTransactions_ImputationFlag": "LibraryServices_CountOf_ReferenceTransactions_ImputationFlag",
                    "RegisteredUsers": "LibraryServices_CountOf_RegisteredUsers",
                    "RegisteredUsers_ImputationFlag": "LibraryServices_CountOf_RegisteredUsers_ImputationFlag",
                }
            },
            "Circulation": {
                "For": {
                    "ChildrenMaterials": "Circulation_For_ChildrenMaterials",
                    "ChildrenMaterials_ImputationFlag": "Circulation_For_ChildrenMaterials_ImputationFlag",
                    "ElectronicMaterials": "Circulation_For_ElectronicMaterials",
                    "ElectronicMaterials_ImputationFlag": "Circulation_For_ElectronicMaterials_ImputationFlag",
                    "PhysicalItems": "Circulation_For_PhysicalItems",
                    "PhysicalItems_ImputationFlag": "Circulation_For_PhysicalItems_ImputationFlag",
                    "ElectronicInfo_SuccessfulRetrieval": "Circulation_For_ElectronicInfo_SuccessfulRetrieval",
                    "ElectronicInfo_SuccessfulRetrieval_ImputationFlag": "Circulation_For_ElectronicInfo_SuccessfulRetrieval_ImputationFlag",
                    "ElectronicContentUse": "Circulation_For_ElectronicContentUse",
                    "ElectronicContentUse_ImputationFlag": "Circulation_For_ElectronicContentUse_ImputationFlag",
                },
                "Total": {
                    "Transactions": "Circulation_Total_Transactions",
                    "Transactions_ImputationFlag": "Circulation_Total_Transactions_ImputationFlag",
                    "CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval": "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval",
                    "CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval_ImputationFlag": "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval_ImputationFlag",
                },
            },
            "InterLibraryLoans": {
                "Amount": {
                    "Given": "InterLibraryLoans_Amount_Given",
                    "Given_ImputationFlag": "InterLibraryLoans_Amount_Given_ImputationFlag",
                    "Received": "InterLibraryLoans_Amount_Received",
                    "Received_ImputationFlag": "InterLibraryLoans_Amount_Received_ImputationFlag",
                }
            },
            "LibraryPrograms": {
                "CountOf": {
                    "For": {
                        "Children": "LibraryPrograms_CountOf_For_Children",
                        "Children_ImputationFlag": "LibraryPrograms_CountOf_For_Children_ImputationFlag",
                        "YoungAdults": "LibraryPrograms_CountOf_For_YoungAdults",
                        "YoungAdults_ImputationFlag": "LibraryPrograms_CountOf_For_YoungAdults_ImputationFlag",
                    },
                    "Total": "LibraryPrograms_CountOf_Total",
                    "Total_ImputationFlag": "LibraryPrograms_CountOf_Total_ImputationFlag",
                },
                "Attendance": {
                    "Total": "LibraryPrograms_Attendance_Total",
                    "Total_ImputationFlag": "LibraryPrograms_Attendance_Total_ImputationFlag",
                    "For": {
                        "Children": "LibraryPrograms_Attendance_For_Children",
                        "Children_ImputationFlag": "LibraryPrograms_Attendance_For_Children_ImputationFlag",
                        "YoungAdults": "LibraryPrograms_Attendance_For_YoungAdults",
                        "YoungAdults_ImputationFlag": "LibraryPrograms_Attendance_For_YoungAdults_ImputationFlag",
                    },
                },
            },
            "OtherElectronicInfo": {
                "CountOf": {
                    "Computers": "OtherElectronicInfo_CountOf_Computers",
                    "Computers_ImputationFlag": "OtherElectronicInfo_CountOf_Computers_ImputationFlag",
                    "ComputerUses": "OtherElectronicInfo_CountOf_ComputerUses",
                    "ComputerUses_ImputationFlag": "OtherElectronicInfo_CountOf_ComputerUses_ImputationFlag",
                    "WiFiSessions": "OtherElectronicInfo_CountOf_WiFiSessions",
                    "WiFiSessions_ImputationFlag": "OtherElectronicInfo_CountOf_WiFiSessions_ImputationFlag",
                    "VisitsToLibraryWebsite": "OtherElectronicInfo_CountOf_VisitsToLibraryWebsite",
                }
            },
            "ReportingPeriod": {
                "StartDate": "ReportingPeriod_StartDate",
                "EndDate": "ReportingPeriod_EndDate",
            },
            "InternationalCommitteeForInformationTechnologyStandardsStateCode_2Digit": "InternationalCommitteeForInformationTechnologyStandardsStateCode_2Digit",
            "SubmissionYearOfPublicLibraryData": "SubmissionYearOfPublicLibraryData",
            "BureauOfEconomicsAnalysisCode": "BureauOfEconomicsAnalysisCode",
        }
    )
    assert lib.system_data_vars == Variables.from_dict(
        {
            "State": "State",
            "Name": "Name",
            "LibraryIdCode": {
                "FromIMLS": "LibraryIdCode_FromIMLS",
                "FromState": "LibraryIdCode_FromState",
            },
            "StreetAddress": {
                "Address": "StreetAddress_Address",
                "City": "StreetAddress_City",
                "ZipCode": "StreetAddress_ZipCode",
                "ZipCode_4Digit": "StreetAddress_ZipCode_4Digit",
            },
            "MailingAddress": {
                "Address": "MailingAddress_Address",
                "City": "MailingAddress_City",
                "ZipCode": "MailingAddress_ZipCode",
                "ZipCode_4Digit": "MailingAddress_ZipCode_4Digit",
                "County": "MailingAddress_County",
                "PhoneNumber": "MailingAddress_PhoneNumber",
            },
            "InterlibraryRelationshipCode": "InterlibraryRelationshipCode",
            "LegalBasisCode": "LegalBasisCode",
            "AdministrativeStructureCode": "AdministrativeStructureCode",
            "MeetsDefinitionOfPublicLibrary": "MeetsDefinitionOfPublicLibrary",
            "TypeOfRegionServed": "TypeOfRegionServed",
            "DidLegalServiceAreaChangeInPastYear": "DidLegalServiceAreaChangeInPastYear",
            "Population": {
                "Of": {
                    "LegalServiceArea": "Population_Of_LegalServiceArea",
                    "LegalServiceArea_ImputationFlag": "Population_Of_LegalServiceArea_ImputationFlag",
                    "LegalServiceArea_Unduplicated": "Population_Of_LegalServiceArea_Unduplicated",
                }
            },
            "ServiceOutlets": {
                "CountOf": {
                    "CentralLibraries": "ServiceOutlets_CountOf_CentralLibraries",
                    "CentralLibraries_ImputationFlag": "ServiceOutlets_CountOf_CentralLibraries_ImputationFlag",
                    "BranchLibraries": "ServiceOutlets_CountOf_BranchLibraries",
                    "BranchLibraries_ImputationFlag": "ServiceOutlets_CountOf_BranchLibraries_ImputationFlag",
                    "Bookmobiles": "ServiceOutlets_CountOf_Bookmobiles",
                    "Bookmobiles_ImputationFlag": "ServiceOutlets_CountOf_Bookmobiles_ImputationFlag",
                }
            },
            "FullTimePaidStaff": {
                "CountOf": {
                    "PaidLibrarians_WithMasters": "FullTimePaidStaff_CountOf_PaidLibrarians_WithMasters",
                    "PaidLibrarians_WithMasters_ImputationFlag": "FullTimePaidStaff_CountOf_PaidLibrarians_WithMasters_ImputationFlag",
                    "Employees_WithTitleLibrarian": "FullTimePaidStaff_CountOf_Employees_WithTitleLibrarian",
                    "Employees_WithTitleLibrarian_ImputationFlag": "FullTimePaidStaff_CountOf_Employees_WithTitleLibrarian_ImputationFlag",
                    "OtherPaidStaff": "FullTimePaidStaff_CountOf_OtherPaidStaff",
                    "OtherPaidStaff_ImputationFlag": "FullTimePaidStaff_CountOf_OtherPaidStaff_ImputationFlag",
                },
                "Total": "FullTimePaidStaff_Total",
                "Total_ImputationFlag": "FullTimePaidStaff_Total_ImputationFlag",
            },
            "OperatingRevenue": {
                "From": {
                    "LocalGovernment": "OperatingRevenue_From_LocalGovernment",
                    "LocalGovernment_ImputationFlag": "OperatingRevenue_From_LocalGovernment_ImputationFlag",
                    "StateGovernment": "OperatingRevenue_From_StateGovernment",
                    "StateGovernment_ImputationFlag": "OperatingRevenue_From_StateGovernment_ImputationFlag",
                    "FederalGovernment": "OperatingRevenue_From_FederalGovernment",
                    "FederalGovernment_ImputationFlag": "OperatingRevenue_From_FederalGovernment_ImputationFlag",
                    "OtherSources": "OperatingRevenue_From_OtherSources",
                    "OtherSources_ImputationFlag": "OperatingRevenue_From_OtherSources_ImputationFlag",
                },
                "Total": "OperatingRevenue_Total",
                "Total_ImputationFlag": "OperatingRevenue_Total_ImputationFlag",
            },
            "OperatingExpenditures": {
                "On": {
                    "Staff": {
                        "Wages": "OperatingExpenditures_On_Staff_Wages",
                        "Wages_ImputationFlag": "OperatingExpenditures_On_Staff_Wages_ImputationFlag",
                        "EmployeeBenefits": "OperatingExpenditures_On_Staff_EmployeeBenefits",
                        "EmployeeBenefits_ImputationFlag": "OperatingExpenditures_On_Staff_EmployeeBenefits_ImputationFlag",
                        "Total": "OperatingExpenditures_On_Staff_Total",
                        "Total_ImputationFlag": "OperatingExpenditures_On_Staff_Total_ImputationFlag",
                    },
                    "Collection": {
                        "PrintMaterials": "OperatingExpenditures_On_Collection_PrintMaterials",
                        "PrintMaterials_ImputationFlag": "OperatingExpenditures_On_Collection_PrintMaterials_ImputationFlag",
                        "ElectronicMaterials": "OperatingExpenditures_On_Collection_ElectronicMaterials",
                        "ElectronicMaterials_ImputationFlag": "OperatingExpenditures_On_Collection_ElectronicMaterials_ImputationFlag",
                        "OtherMaterials": "OperatingExpenditures_On_Collection_OtherMaterials",
                        "OtherMaterials_ImputationFlag": "OperatingExpenditures_On_Collection_OtherMaterials_ImputationFlag",
                        "Total": "OperatingExpenditures_On_Collection_Total",
                        "Total_ImputationFlag": "OperatingExpenditures_On_Collection_Total_ImputationFlag",
                    },
                    "Other": "OperatingExpenditures_On_Other",
                    "Other_ImputationFlag": "OperatingExpenditures_On_Other_ImputationFlag",
                },
                "Total": "OperatingExpenditures_Total",
                "Total_ImputationFlag": "OperatingExpenditures_Total_ImputationFlag",
            },
            "CapitalRevenue": {
                "From": {
                    "LocalGovernment": "CapitalRevenue_From_LocalGovernment",
                    "Government_ImputationFlag": "CapitalRevenue_From_Government_ImputationFlag",
                    "StateGovernment": "CapitalRevenue_From_StateGovernment",
                    "StateGovernment_ImputationFlag": "CapitalRevenue_From_StateGovernment_ImputationFlag",
                    "FederalGovernment": "CapitalRevenue_From_FederalGovernment",
                    "FederalGovernment_ImputationFlag": "CapitalRevenue_From_FederalGovernment_ImputationFlag",
                    "Other": "CapitalRevenue_From_Other",
                    "Other_ImputationFlag": "CapitalRevenue_From_Other_ImputationFlag",
                },
                "Total": "CapitalRevenue_Total",
                "Total_ImputationFlag": "CapitalRevenue_Total_ImputationFlag",
            },
            "CapitalExpenditures": {
                "Total": "CapitalExpenditures_Total",
                "Total_ImputationFlag": "CapitalExpenditures_Total_ImputationFlag",
            },
            "LibraryCollection": {
                "CountOf": {
                    "PrintMaterials": "LibraryCollection_CountOf_PrintMaterials",
                    "PrintMaterials_ImputationFlag": "LibraryCollection_CountOf_PrintMaterials_ImputationFlag",
                    "ElectronicMaterials": "LibraryCollection_CountOf_ElectronicMaterials",
                    "ElectronicMaterials_ImputationFlag": "LibraryCollection_CountOf_ElectronicMaterials_ImputationFlag",
                    "AudioMaterials_Physical": "LibraryCollection_CountOf_AudioMaterials_Physical",
                    "AudioMaterials_Physical_ImputationFlag": "LibraryCollection_CountOf_AudioMaterials_Physical_ImputationFlag",
                    "AudioMaterials_Downloadable": "LibraryCollection_CountOf_AudioMaterials_Downloadable",
                    "AudioMaterials_Downloadable_ImputationFlag": "LibraryCollection_CountOf_AudioMaterials_Downloadable_ImputationFlag",
                    "VideoMaterials_Physical": "LibraryCollection_CountOf_VideoMaterials_Physical",
                    "VideoMaterials_Physical_ImputationFlag": "LibraryCollection_CountOf_VideoMaterials_Physical_ImputationFlag",
                    "VideoMaterials_Downloadable": "LibraryCollection_CountOf_VideoMaterials_Downloadable",
                    "VideoMaterials_Downloadable_ImputationFlag": "LibraryCollection_CountOf_VideoMaterials_Downloadable_ImputationFlag",
                }
            },
            "ElectronicCollection": {
                "From": {
                    "LocalOrOther": "ElectronicCollection_From_LocalOrOther",
                    "LocalOrOther_ImputationFlag": "ElectronicCollection_From_LocalOrOther_ImputationFlag",
                    "State": "ElectronicCollection_From_State",
                    "State_ImputationFlag": "ElectronicCollection_From_State_ImputationFlag",
                },
                "Total": "ElectronicCollection_Total",
                "Total_ImputationFlag": "ElectronicCollection_Total_ImputationFlag",
            },
            "PrintSerialSubscriptions": {
                "Total": "PrintSerialSubscriptions_Total",
                "Total_ImputationFlag": "PrintSerialSubscriptions_Total_ImputationFlag",
            },
            "PublicServiceHours": {
                "Total_PerYear": "PublicServiceHours_Total_PerYear",
                "Total_PerYear_ImputationFlag": "PublicServiceHours_Total_PerYear_ImputationFlag",
            },
            "LibraryServices": {
                "CountOf": {
                    "Visits": "LibraryServices_CountOf_Visits",
                    "Visits_ImputationFlag": "LibraryServices_CountOf_Visits_ImputationFlag",
                    "ReferenceTransactions": "LibraryServices_CountOf_ReferenceTransactions",
                    "ReferenceTransactions_ImputationFlag": "LibraryServices_CountOf_ReferenceTransactions_ImputationFlag",
                    "RegisteredUsers": "LibraryServices_CountOf_RegisteredUsers",
                    "RegisteredUsers_ImputationFlag": "LibraryServices_CountOf_RegisteredUsers_ImputationFlag",
                }
            },
            "Circulation": {
                "CountOf": {
                    "ChildrenMaterials": "Circulation_CountOf_ChildrenMaterials",
                    "ChildrenMaterials_ImputationFlag": "Circulation_CountOf_ChildrenMaterials_ImputationFlag",
                    "ElectronicMaterials": "Circulation_CountOf_ElectronicMaterials",
                    "ElectronicMaterials_ImputationFlag": "Circulation_CountOf_ElectronicMaterials_ImputationFlag",
                    "PhysicalMaterials": "Circulation_CountOf_PhysicalMaterials",
                    "PhysicalMaterials_ImputationFlag": "Circulation_CountOf_PhysicalMaterials_ImputationFlag",
                    "SuccessfulRetrievalOfElectronicInfo": "Circulation_CountOf_SuccessfulRetrievalOfElectronicInfo",
                    "SuccessfulRetrievalOfElectronicInfo_ImputationFlag": "Circulation_CountOf_SuccessfulRetrievalOfElectronicInfo_ImputationFlag",
                    "ElectronicContentUse": "Circulation_CountOf_ElectronicContentUse",
                    "ElectronicContentUse_ImputationFlag": "Circulation_CountOf_ElectronicContentUse_ImputationFlag",
                },
                "Total": {
                    "Transactions": "Circulation_Total_Transactions",
                    "Transactions_ImputationFlag": "Circulation_Total_Transactions_ImputationFlag",
                    "CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval": "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval",
                    "CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval_ImputationFlag": "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval_ImputationFlag",
                },
            },
            "InterLibraryLoans": {
                "Amount": {
                    "Given": "InterLibraryLoans_Amount_Given",
                    "Given_ImputationFlag": "InterLibraryLoans_Amount_Given_ImputationFlag",
                    "Received": "InterLibraryLoans_Amount_Received",
                    "Received_ImputationFlag": "InterLibraryLoans_Amount_Received_ImputationFlag",
                }
            },
            "LibraryPrograms": {
                "CountOf": {
                    "For": {
                        "Children": "LibraryPrograms_CountOf_For_Children",
                        "Children_ImputationFlag": "LibraryPrograms_CountOf_For_Children_ImputationFlag",
                        "YoungAdults": "LibraryPrograms_CountOf_For_YoungAdults",
                        "YoungAdults_ImputationFlag": "LibraryPrograms_CountOf_For_YoungAdults_ImputationFlag",
                    },
                    "Total": "LibraryPrograms_CountOf_Total",
                    "Total_ImputationFlag": "LibraryPrograms_CountOf_Total_ImputationFlag",
                },
                "Attendance": {
                    "Total": "LibraryPrograms_Attendance_Total",
                    "Total_ImputationFlag": "LibraryPrograms_Attendance_Total_ImputationFlag",
                    "For": {
                        "Children": "LibraryPrograms_Attendance_For_Children",
                        "Children_ImputationFlag": "LibraryPrograms_Attendance_For_Children_ImputationFlag",
                        "YoungAdults": "LibraryPrograms_Attendance_For_YoungAdults",
                        "YoungAdults_ImputationFlag": "LibraryPrograms_Attendance_For_YoungAdults_ImputationFlag",
                    },
                },
            },
            "OtherElectronicInformation": {
                "CountOf": {
                    "ComputersUsedByPublic": "OtherElectronicInformation_CountOf_ComputersUsedByPublic",
                    "ComputersUsedByPublic_ImputationFlag": "OtherElectronicInformation_CountOf_ComputersUsedByPublic_ImputationFlag",
                    "UsagesOfComputers": "OtherElectronicInformation_CountOf_UsagesOfComputers",
                    "UsagesOfComputers_ImputationFlag": "OtherElectronicInformation_CountOf_UsagesOfComputers_ImputationFlag",
                    "WiFiUses": "OtherElectronicInformation_CountOf_WiFiUses",
                    "WiFiUses_ImputationFlag": "OtherElectronicInformation_CountOf_WiFiUses_ImputationFlag",
                    "VisitsToLibraryWebsite": "OtherElectronicInformation_CountOf_VisitsToLibraryWebsite",
                }
            },
            "ReportingPeriod": {
                "StartDate": "ReportingPeriod_StartDate",
                "EndDate": "ReportingPeriod_EndDate",
            },
            "SubmissionYearOfPublicLibraryData": "SubmissionYearOfPublicLibraryData",
            "BureauOfEconomicAnalysisCode": "BureauOfEconomicAnalysisCode",
            "ReportingStatus": "ReportingStatus",
            "StructureChangeCode": "StructureChangeCode",
            "NameChangeCode": "NameChangeCode",
            "AddressChangeCode": "AddressChangeCode",
            "Longitute": "Longitute",
            "Latitude": "Latitude",
            "InternationalCommitteeForInfoTechStandardsStateCode_2Digit": "InternationalCommitteeForInfoTechStandardsStateCode_2Digit",
            "InternationalCommitteeForInfoTechStandardsStateCode_3Digit": "InternationalCommitteeForInfoTechStandardsStateCode_3Digit",
            "GeographicNamesInformationSystemFeatureId": "GeographicNamesInformationSystemFeatureId",
            "CountyPopulation": "CountyPopulation",
            "CateorizationOfLocale": {
                "CategorizationBySizeAndProximityToCities": "CateorizationOfLocale_CategorizationBySizeAndProximityToCities",
                "CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets": "CateorizationOfLocale_CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets",
                "CategorizationBySizeAndProximityToCities_FromRuralEducationAchievementProgram": "CateorizationOfLocale_CategorizationBySizeAndProximityToCities_FromRuralEducationAchievementProgram",
                "CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets_FromRuralEducationAchievementProgram": "CateorizationOfLocale_CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets_FromRuralEducationAchievementProgram",
            },
            "CensusTract": "CensusTract",
            "CensusBlock": "CensusBlock",
            "CongressionalDistrict": "CongressionalDistrict",
            "CoreBasedStatisticalArea": "CoreBasedStatisticalArea",
            "MetropolitanAndMicropolitcanStatisticalAreaFlag": "MetropolitanAndMicropolitcanStatisticalAreaFlag",
            "Geocoding_AccuraryAndPrecision": "Geocoding_AccuraryAndPrecision",
        }
    )
    assert lib.outlet_data_vars == Variables.from_dict(
        {
            "State": "State",
            "LibraryIdCode": {
                "FromIMLS": "LibraryIdCode_FromIMLS",
                "Suffix": "LibraryIdCode_Suffix",
                "FromState": "LibraryIdCode_FromState",
            },
            "MeetsDefinitionOfPublicLibrary": "MeetsDefinitionOfPublicLibrary",
            "Name": "Name",
            "StreetAddress": {
                "Address": "StreetAddress_Address",
                "City": "StreetAddress_City",
                "ZipCode": "StreetAddress_ZipCode",
                "ZipCode_4Digit": "StreetAddress_ZipCode_4Digit",
                "County": "StreetAddress_County",
                "Phone": "StreetAddress_Phone",
            },
            "OutletType": "OutletType",
            "SquareFootage": "SquareFootage",
            "SquareFootage_ImputationFlag": "SquareFootage_ImputationFlag",
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

    assert lib.new_col_to_original_col_mapping == {
        DatafileType.OutletData: {
            "AddressChangeCode": "STATADDR",
            "BureauOfEconomicsAnalysisCode": "OBEREG",
            "CategorizationOfLocale_BySizeAndProximityToCities": "LOCALE",
            "CategorizationOfLocale_BySizeAndProximityToCities_FromRuralEducationAchievementProgram": "REAPLOCALE",
            "CensusBlock": "CENBLOCK",
            "CensusTract": "CENTRACT",
            "CongressionalDistrict": "CDCODE",
            "CoreBasedStatisticalArea": "CBSA",
            "CountyPopulation": "CNTYPOP",
            "Geocoding_AccuracyAndPrecision": "GEOMATCH",
            "GeographicNamesInformationSystemFeatureId": "GNISPLAC",
            "HoursOpen": "HOURS",
            "InternationalCommiteeForInfoTechStandardsStateCode_ThreeDigit": "INCITSCO",
            "InternationalCommiteeForInfoTechStandardsStateCode_TwoDigit": "INCITSST",
            "Latitude": "LATITUDE",
            "LibraryIdCode_FromIMLS": "FSCSKEY",
            "LibraryIdCode_FromState": "LIBID",
            "LibraryIdCode_Suffix": "FSCS_SEQ",
            "Longitude": "LONGITUD",
            "MeetsDefinitionOfPublicLibrary": "C_FSCS",
            "MetropolitanAndMicropolitcanStatisticalAreaFlag": "MICROF",
            "Name": "LIBNAME",
            "NameChangeCode": "STATNAME",
            "Num_BookmobilesInBookmobileOutletRecord": "L_NUM_BM",
            "OutletType": "C_OUT_TY",
            "SquareFootage": "SQ_FEET",
            "SquareFootage_ImputationFlag": "F_SQ_FT",
            "State": "STABR",
            "StreetAddress_Address": "ADDRESS",
            "StreetAddress_City": "CITY",
            "StreetAddress_County": "CNTY",
            "StreetAddress_Phone": "PHONE",
            "StreetAddress_ZipCode": "ZIP",
            "StreetAddress_ZipCode_4Digit": "ZIP4",
            "StructureChangeCode": "STATSTRU",
            "SubmissionYearOfPublicLibraryData": "YR_SUB",
            "WeeksOpen": "WKS_OPEN",
        },
        DatafileType.SummaryData: {
            "BureauOfEconomicsAnalysisCode": "OBEREG",
            "CapitalExpenditures_Total": "CAPITAL",
            "CapitalExpenditures_Total_ImputationFlag": "F_TCAPX",
            "CapitalRevenue_From_FederalGovernment": "FCAP_REV",
            "CapitalRevenue_From_FederalGovernment_ImputationFlag": "F_FCAPRV",
            "CapitalRevenue_From_LocalGovernment": "LCAP_REV",
            "CapitalRevenue_From_LocalGovernment_ImputationFlag": "F_LCAPRV",
            "CapitalRevenue_From_Other": "OCAP_REV",
            "CapitalRevenue_From_Other_ImputationFlag": "F_OCAPRV",
            "CapitalRevenue_From_State": "SCAP_REV",
            "CapitalRevenue_From_State_ImputationFlag": "F_SCAPRV",
            "CapitalRevenue_Total": "CAP_REV",
            "CapitalRevenue_Total_ImputationFlag": "F_TCAPRV",
            "Circulation_For_ChildrenMaterials": "KIDCIRCL",
            "Circulation_For_ChildrenMaterials_ImputationFlag": "F_KIDCIR",
            "Circulation_For_ElectronicContentUse": "ELCONT",
            "Circulation_For_ElectronicContentUse_ImputationFlag": "F_ELCONT",
            "Circulation_For_ElectronicInfo_SuccessfulRetrieval": "ELINFO",
            "Circulation_For_ElectronicInfo_SuccessfulRetrieval_ImputationFlag": "F_ELINFO",
            "Circulation_For_ElectronicMaterials": "ELMATCIR",
            "Circulation_For_ElectronicMaterials_ImputationFlag": "F_EMTCIR",
            "Circulation_For_PhysicalItems": "PHYSCIR",
            "Circulation_For_PhysicalItems_ImputationFlag": "F_PHYSCR",
            "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval": "TOTCOLL",
            "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval_ImputationFlag": "F_TOTCOL",
            "Circulation_Total_Transactions": "TOTCIR",
            "Circulation_Total_Transactions_ImputationFlag": "F_TOTCIR",
            "ElectronicCollections_From_LocalOrOther": "EC_LO_OT",
            "ElectronicCollections_From_Other_ImputationFlag": "F_EC_L_O",
            "ElectronicCollections_From_State": "EC_ST",
            "ElectronicCollections_From_State_ImputationFlag": "F_EC_ST",
            "ElectronicCollections_Total": "ELECCOLL",
            "ElectronicCollections_Total_ImputationFlag": "F_ELECOL",
            "FullTimePaidStaff_Librarians": "LIBRARIA",
            "FullTimePaidStaff_Librarians_ImputationFlag": "F_LIBRAR",
            "FullTimePaidStaff_Librarians_WithMasters": "MASTER",
            "FullTimePaidStaff_Librarians_WithMasters_ImputationFlag": "F_MASTER",
            "FullTimePaidStaff_Other": "OTHPAID",
            "FullTimePaidStaff_Other_ImputationFlag": "F_OTHSTF",
            "FullTimePaidStaff_Total": "TOTSTAFF",
            "FullTimePaidStaff_Total_ImputationFlag": "F_TOTSTF",
            "Hours_Total": "HRS_OPEN",
            "Hours_Total_ImputationFlag": "F_HRS_OP",
            "InterLibraryLoans_Amount_Given": "LOANTO",
            "InterLibraryLoans_Amount_Given_ImputationFlag": "F_LOANTO",
            "InterLibraryLoans_Amount_Received": "LOANFM",
            "InterLibraryLoans_Amount_Received_ImputationFlag": "F_LOANFM",
            "InternationalCommitteeForInformationTechnologyStandardsStateCode_2Digit": "INCITSST",
            "LibraryCollections_CountOf_AudioPhysical_ImputationFlag": "F_AUD_PH",
            "LibraryCollections_CountOf_Audio_Downloadable": "AUDIO_DL",
            "LibraryCollections_CountOf_Audio_Downloadable_ImputationFlag": "F_AUD_DL",
            "LibraryCollections_CountOf_Audio_Physical": "AUDIO_PH",
            "LibraryCollections_CountOf_EBooks": "EBOOK",
            "LibraryCollections_CountOf_EBooks_ImputationFlag": "F_EBOOK",
            "LibraryCollections_CountOf_PrintMaterials": "BKVOL",
            "LibraryCollections_CountOf_PrintMaterials_ImputationFlag": "F_BKVOL",
            "LibraryCollections_CountOf_Video_Downloadable": "VIDEO_DL",
            "LibraryCollections_CountOf_Video_Downloadable_ImputationFlag": "F_VID_DL",
            "LibraryCollections_CountOf_Video_Physical": "VIDEO_PH",
            "LibraryCollections_CountOf_Video_Physical_ImputationFlag": "F_VID_PH",
            "LibraryPrograms_Attendance_For_Children": "KIDATTEN",
            "LibraryPrograms_Attendance_For_Children_ImputationFlag": "F_KIDATT",
            "LibraryPrograms_Attendance_For_YoungAdults": "YAATTEN",
            "LibraryPrograms_Attendance_For_YoungAdults_ImputationFlag": "F_YAATT",
            "LibraryPrograms_Attendance_Total": "TOTATTEN",
            "LibraryPrograms_Attendance_Total_ImputationFlag": "F_TOTATT",
            "LibraryPrograms_CountOf_For_Children": "KIDPRO",
            "LibraryPrograms_CountOf_For_Children_ImputationFlag": "F_KIDPRO",
            "LibraryPrograms_CountOf_For_YoungAdults": "YAPRO",
            "LibraryPrograms_CountOf_For_YoungAdults_ImputationFlag": "F_YAPRO",
            "LibraryPrograms_CountOf_Total": "TOTPRO",
            "LibraryPrograms_CountOf_Total_ImputationFlag": "F_TOTPRO",
            "LibraryServices_CountOf_ReferenceTransactions": "REFERENC",
            "LibraryServices_CountOf_ReferenceTransactions_ImputationFlag": "F_REFER",
            "LibraryServices_CountOf_RegisteredUsers": "REGBOR",
            "LibraryServices_CountOf_RegisteredUsers_ImputationFlag": "F_REGBOR",
            "LibraryServices_CountOf_Visits": "VISITS",
            "LibraryServices_CountOf_Visits_ImputationFlag": "F_VISITS",
            "Name": "STABR",
            "OperatingExpenditures_On_Collections_Of_ElectronicMaterials": "ELMATEXP",
            "OperatingExpenditures_On_Collections_Of_ElectronicMaterials_ImputationFlag": "F_ELMATX",
            "OperatingExpenditures_On_Collections_Of_OtherMaterials": "OTHMATEX",
            "OperatingExpenditures_On_Collections_Of_OtherMaterials_ImputationFlag": "F_OTMATX",
            "OperatingExpenditures_On_Collections_Of_PrintMaterials": "PRMATEXP",
            "OperatingExpenditures_On_Collections_Of_PrintMaterials_ImputationFlag": "F_PRMATX",
            "OperatingExpenditures_On_Collections_Of_Total": "TOTEXPCO",
            "OperatingExpenditures_On_Collections_Of_Total_ImputationFlag": "F_TOCOLX",
            "OperatingExpenditures_On_Other": "OTHOPEXP",
            "OperatingExpenditures_On_Other_ImputationFlag": "F_OTHOPX",
            "OperatingExpenditures_On_Staff_EmployeeBenefits": "BENEFIT",
            "OperatingExpenditures_On_Staff_EmployeeBenefits_ImputationFlag": "F_BENX",
            "OperatingExpenditures_On_Staff_Salaries": "SALARIES",
            "OperatingExpenditures_On_Staff_Salaries_ImputationFlag": "F_SALX",
            "OperatingExpenditures_On_Staff_Total": "STAFFEXP",
            "OperatingExpenditures_On_Staff_Total_ImputationFlag": "F_TOSTFX",
            "OperatingExpenditures_Total": "TOTOPEXP",
            "OperatingExpenditures_Total_ImputationFlag": "F_TOTOPX",
            "OperatingRevenue_From_FederalGovernment": "FEDGVT",
            "OperatingRevenue_From_FederalGovernment_ImputationFlag": "F_FEDGVT",
            "OperatingRevenue_From_LocalGovernment": "LOCGVT",
            "OperatingRevenue_From_LocalGovernment_ImputationFlag": "F_LOCGVT",
            "OperatingRevenue_From_Other": "OTHINCM",
            "OperatingRevenue_From_Other_ImputationFlag": "F_OTHINC",
            "OperatingRevenue_From_StateGovernment": "STGVT",
            "OperatingRevenue_From_StateGovernment_ImputationFlag": "F_STGVT",
            "OperatingRevenue_Total": "TOTINCM",
            "OperatingRevenue_Total_ImputationFlag": "F_TOTINC",
            "OtherCollections_CurrentPrintSerialSubscriptions": "SUBSCRIP",
            "OtherCollections_CurrentPrintSerialSubscriptions_ImputationFlag": "F_PRSUB",
            "OtherElectronicInfo_CountOf_ComputerUses": "PITUSR",
            "OtherElectronicInfo_CountOf_ComputerUses_ImputationFlag": "F_PITUSR",
            "OtherElectronicInfo_CountOf_Computers": "GPTERMS",
            "OtherElectronicInfo_CountOf_Computers_ImputationFlag": "F_GPTERM",
            "OtherElectronicInfo_CountOf_VisitsToLibraryWebsite": "WEBVISIT",
            "OtherElectronicInfo_CountOf_WiFiSessions": "WIFISESS",
            "OtherElectronicInfo_CountOf_WiFiSessions_ImputationFlag": "F_WIFISS",
            "Population_Of_LegalServiceArea": "POPU_LSA",
            "Population_Of_LegalServiceArea_ImputationFlag": "F_POPLSA",
            "Population_Of_LegalServiceAreas_Unduplicated": "POPU_UND",
            "Population_Of_State_EstimateTotal": "POPU_ST",
            "ReportingPeriod_EndDate": "ENDDATE",
            "ReportingPeriod_StartDate": "STARTDAT",
            "ServiceOutlets_CountOf_Bookmobiles": "BKMOB",
            "ServiceOutlets_CountOf_Bookmobiles_ImputationFlag": "F_BKMOB",
            "ServiceOutlets_CountOf_BranchLibraries": "BRANLIB",
            "ServiceOutlets_CountOf_BranchLibraries_ImputationFlag": "F_BRLIB",
            "ServiceOutlets_CountOf_CentralLibraries": "CENTLIB",
            "ServiceOutlets_CountOf_CentralLibraries_ImputationFlag": "F_CENLIB",
            "SubmissionYearOfPublicLibraryData": "YR_SUB",
        },
        DatafileType.SystemData: {
            "AddressChangeCode": "STATADDR",
            "AdministrativeStructureCode": "C_ADMIN",
            "BureauOfEconomicAnalysisCode": "OBEREG",
            "CapitalExpenditures_Total": "CAPITAL",
            "CapitalExpenditures_Total_ImputationFlag": "F_TCAPX",
            "CapitalRevenue_From_FederalGovernment": "FCAP_REV",
            "CapitalRevenue_From_FederalGovernment_ImputationFlag": "F_FCAPRV",
            "CapitalRevenue_From_Government_ImputationFlag": "F_LCAPRV",
            "CapitalRevenue_From_LocalGovernment": "LCAP_REV",
            "CapitalRevenue_From_Other": "OCAP_REV",
            "CapitalRevenue_From_Other_ImputationFlag": "F_OCAPRV",
            "CapitalRevenue_From_StateGovernment": "SCAP_REV",
            "CapitalRevenue_From_StateGovernment_ImputationFlag": "F_SCAPRV",
            "CapitalRevenue_Total": "CAP_REV",
            "CapitalRevenue_Total_ImputationFlag": "F_TCAPRV",
            "CateorizationOfLocale_CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets": "LOCALE_MOD",
            "CateorizationOfLocale_CategorizationByModalLocaleCodeOfAssociatedStationaryOutlets_FromRuralEducationAchievementProgram": "REAPLOCALE_MOD",
            "CateorizationOfLocale_CategorizationBySizeAndProximityToCities": "LOCALE_ADD",
            "CateorizationOfLocale_CategorizationBySizeAndProximityToCities_FromRuralEducationAchievementProgram": "REAPLOCALE_ADD",
            "CensusBlock": "CENBLOCK",
            "CensusTract": "CENTRACT",
            "Circulation_CountOf_ChildrenMaterials": "KIDCIRCL",
            "Circulation_CountOf_ChildrenMaterials_ImputationFlag": "F_KIDCIR",
            "Circulation_CountOf_ElectronicContentUse": "ELCONT",
            "Circulation_CountOf_ElectronicContentUse_ImputationFlag": "F_ELCONT",
            "Circulation_CountOf_ElectronicMaterials": "ELMATCIR",
            "Circulation_CountOf_ElectronicMaterials_ImputationFlag": "F_EMTCIR",
            "Circulation_CountOf_PhysicalMaterials": "PHYSCIR",
            "Circulation_CountOf_PhysicalMaterials_ImputationFlag": "F_PHYSCR",
            "Circulation_CountOf_SuccessfulRetrievalOfElectronicInfo": "ELINFO",
            "Circulation_CountOf_SuccessfulRetrievalOfElectronicInfo_ImputationFlag": "F_ELINFO",
            "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval": "TOTCOLL",
            "Circulation_Total_CountOf_PhysicalAndElectronicCirculation_And_ElectronicSuccessfulRetrieval_ImputationFlag": "F_TOTCOL",
            "Circulation_Total_Transactions": "TOTCIR",
            "Circulation_Total_Transactions_ImputationFlag": "F_TOTCIR",
            "CongressionalDistrict": "CDCODE",
            "CoreBasedStatisticalArea": "CBSA",
            "CountyPopulation": "CNTYPOP",
            "DidLegalServiceAreaChangeInPastYear": "LSABOUND",
            "ElectronicCollection_From_LocalOrOther": "EC_LO_OT",
            "ElectronicCollection_From_LocalOrOther_ImputationFlag": "F_EC_L_O",
            "ElectronicCollection_From_State": "EC_ST",
            "ElectronicCollection_From_State_ImputationFlag": "F_EC_ST",
            "ElectronicCollection_Total": "ELECCOLL",
            "ElectronicCollection_Total_ImputationFlag": "F_ELECOL",
            "FullTimePaidStaff_CountOf_Employees_WithTitleLibrarian": "LIBRARIA",
            "FullTimePaidStaff_CountOf_Employees_WithTitleLibrarian_ImputationFlag": "F_LIBRAR",
            "FullTimePaidStaff_CountOf_OtherPaidStaff": "OTHPAID",
            "FullTimePaidStaff_CountOf_OtherPaidStaff_ImputationFlag": "F_OTHSTF",
            "FullTimePaidStaff_CountOf_PaidLibrarians_WithMasters": "MASTER",
            "FullTimePaidStaff_CountOf_PaidLibrarians_WithMasters_ImputationFlag": "F_MASTER",
            "FullTimePaidStaff_Total": "TOTSTAFF",
            "FullTimePaidStaff_Total_ImputationFlag": "F_TOTSTF",
            "Geocoding_AccuraryAndPrecision": "GEOMATCH",
            "GeographicNamesInformationSystemFeatureId": "GNISPLAC",
            "InterLibraryLoans_Amount_Given": "LOANTO",
            "InterLibraryLoans_Amount_Given_ImputationFlag": "F_LOANTO",
            "InterLibraryLoans_Amount_Received": "LOANFM",
            "InterLibraryLoans_Amount_Received_ImputationFlag": "F_LOANFM",
            "InterlibraryRelationshipCode": "C_RELATN",
            "InternationalCommitteeForInfoTechStandardsStateCode_2Digit": "INCITSST",
            "InternationalCommitteeForInfoTechStandardsStateCode_3Digit": "INCITSCO",
            "Latitude": "LATITUDE",
            "LegalBasisCode": "C_LEGBAS",
            "LibraryCollection_CountOf_AudioMaterials_Downloadable": "AUDIO_DL",
            "LibraryCollection_CountOf_AudioMaterials_Downloadable_ImputationFlag": "F_AUD_DL",
            "LibraryCollection_CountOf_AudioMaterials_Physical": "AUDIO_PH",
            "LibraryCollection_CountOf_AudioMaterials_Physical_ImputationFlag": "F_AUD_PH",
            "LibraryCollection_CountOf_ElectronicMaterials": "EBOOK",
            "LibraryCollection_CountOf_ElectronicMaterials_ImputationFlag": "F_EBOOK",
            "LibraryCollection_CountOf_PrintMaterials": "BKVOL",
            "LibraryCollection_CountOf_PrintMaterials_ImputationFlag": "F_BKVOL",
            "LibraryCollection_CountOf_VideoMaterials_Downloadable": "VIDEO_DL",
            "LibraryCollection_CountOf_VideoMaterials_Downloadable_ImputationFlag": "F_VID_DL",
            "LibraryCollection_CountOf_VideoMaterials_Physical": "VIDEO_PH",
            "LibraryCollection_CountOf_VideoMaterials_Physical_ImputationFlag": "F_VID_PH",
            "LibraryIdCode_FromIMLS": "FSCSKEY",
            "LibraryIdCode_FromState": "LIBID",
            "LibraryPrograms_Attendance_For_Children": "KIDATTEN",
            "LibraryPrograms_Attendance_For_Children_ImputationFlag": "F_KIDATT",
            "LibraryPrograms_Attendance_For_YoungAdults": "YAATTEN",
            "LibraryPrograms_Attendance_For_YoungAdults_ImputationFlag": "F_YAATT",
            "LibraryPrograms_Attendance_Total": "TOTATTEN",
            "LibraryPrograms_Attendance_Total_ImputationFlag": "F_TOTATT",
            "LibraryPrograms_CountOf_For_Children": "KIDPRO",
            "LibraryPrograms_CountOf_For_Children_ImputationFlag": "F_KIDPRO",
            "LibraryPrograms_CountOf_For_YoungAdults": "YAPRO",
            "LibraryPrograms_CountOf_For_YoungAdults_ImputationFlag": "F_YAPRO",
            "LibraryPrograms_CountOf_Total": "TOTPRO",
            "LibraryPrograms_CountOf_Total_ImputationFlag": "F_TOTPRO",
            "LibraryServices_CountOf_ReferenceTransactions": "REFERENC",
            "LibraryServices_CountOf_ReferenceTransactions_ImputationFlag": "F_REFER",
            "LibraryServices_CountOf_RegisteredUsers": "REGBOR",
            "LibraryServices_CountOf_RegisteredUsers_ImputationFlag": "F_REGBOR",
            "LibraryServices_CountOf_Visits": "VISITS",
            "LibraryServices_CountOf_Visits_ImputationFlag": "F_VISITS",
            "Longitute": "LONGITUD",
            "MailingAddress_Address": "ADDRES_M",
            "MailingAddress_City": "CITY_M",
            "MailingAddress_County": "CNTY",
            "MailingAddress_PhoneNumber": "PHONE",
            "MailingAddress_ZipCode": "ZIP_M",
            "MailingAddress_ZipCode_4Digit": "ZIP4_M",
            "MeetsDefinitionOfPublicLibrary": "C_FSCS",
            "MetropolitanAndMicropolitcanStatisticalAreaFlag": "MICROF",
            "Name": "LIBNAME",
            "NameChangeCode": "STATNAME",
            "OperatingExpenditures_On_Collection_ElectronicMaterials": "ELMATEXP",
            "OperatingExpenditures_On_Collection_ElectronicMaterials_ImputationFlag": "F_ELMATX",
            "OperatingExpenditures_On_Collection_OtherMaterials": "OTHMATEX",
            "OperatingExpenditures_On_Collection_OtherMaterials_ImputationFlag": "F_OTMATX",
            "OperatingExpenditures_On_Collection_PrintMaterials": "PRMATEXP",
            "OperatingExpenditures_On_Collection_PrintMaterials_ImputationFlag": "F_PRMATX",
            "OperatingExpenditures_On_Collection_Total": "TOTEXPCO",
            "OperatingExpenditures_On_Collection_Total_ImputationFlag": "F_TOCOLX",
            "OperatingExpenditures_On_Other": "OTHOPEXP",
            "OperatingExpenditures_On_Other_ImputationFlag": "F_OTHOPX",
            "OperatingExpenditures_On_Staff_EmployeeBenefits": "BENEFIT",
            "OperatingExpenditures_On_Staff_EmployeeBenefits_ImputationFlag": "F_BENX",
            "OperatingExpenditures_On_Staff_Total": "STAFFEXP",
            "OperatingExpenditures_On_Staff_Total_ImputationFlag": "F_TOSTFX",
            "OperatingExpenditures_On_Staff_Wages": "SALARIES",
            "OperatingExpenditures_On_Staff_Wages_ImputationFlag": "F_SALX",
            "OperatingExpenditures_Total": "TOTOPEXP",
            "OperatingExpenditures_Total_ImputationFlag": "F_TOTOPX",
            "OperatingRevenue_From_FederalGovernment": "FEDGVT",
            "OperatingRevenue_From_FederalGovernment_ImputationFlag": "F_FEDGVT",
            "OperatingRevenue_From_LocalGovernment": "LOCGVT",
            "OperatingRevenue_From_LocalGovernment_ImputationFlag": "F_LOCGVT",
            "OperatingRevenue_From_OtherSources": "OTHINCM",
            "OperatingRevenue_From_OtherSources_ImputationFlag": "F_OTHINC",
            "OperatingRevenue_From_StateGovernment": "STGVT",
            "OperatingRevenue_From_StateGovernment_ImputationFlag": "F_STGVT",
            "OperatingRevenue_Total": "TOTINCM",
            "OperatingRevenue_Total_ImputationFlag": "F_TOTINC",
            "OtherElectronicInformation_CountOf_ComputersUsedByPublic": "GPTERMS",
            "OtherElectronicInformation_CountOf_ComputersUsedByPublic_ImputationFlag": "F_GPTERM",
            "OtherElectronicInformation_CountOf_UsagesOfComputers": "PITUSR",
            "OtherElectronicInformation_CountOf_UsagesOfComputers_ImputationFlag": "F_PITUSR",
            "OtherElectronicInformation_CountOf_VisitsToLibraryWebsite": "WEBVISIT",
            "OtherElectronicInformation_CountOf_WiFiUses": "WIFISESS",
            "OtherElectronicInformation_CountOf_WiFiUses_ImputationFlag": "F_WIFISS",
            "Population_Of_LegalServiceArea": "POPU_LSA",
            "Population_Of_LegalServiceArea_ImputationFlag": "F_POPLSA",
            "Population_Of_LegalServiceArea_Unduplicated": "POPU_UND",
            "PrintSerialSubscriptions_Total": "SUBSCRIP",
            "PrintSerialSubscriptions_Total_ImputationFlag": "F_PRSUB",
            "PublicServiceHours_Total_PerYear": "HRS_OPEN",
            "PublicServiceHours_Total_PerYear_ImputationFlag": "F_HRS_OP",
            "ReportingPeriod_EndDate": "ENDDATE",
            "ReportingPeriod_StartDate": "STARTDAT",
            "ReportingStatus": "RSTATUS",
            "ServiceOutlets_CountOf_Bookmobiles": "BKMOB",
            "ServiceOutlets_CountOf_Bookmobiles_ImputationFlag": "F_BKMOB",
            "ServiceOutlets_CountOf_BranchLibraries": "BRANLIB",
            "ServiceOutlets_CountOf_BranchLibraries_ImputationFlag": "F_BRLIB",
            "ServiceOutlets_CountOf_CentralLibraries": "CENTLIB",
            "ServiceOutlets_CountOf_CentralLibraries_ImputationFlag": "F_CENLIB",
            "State": "STABR",
            "StreetAddress_Address": "ADDRESS",
            "StreetAddress_City": "CITY",
            "StreetAddress_ZipCode": "ZIP",
            "StreetAddress_ZipCode_4Digit": "ZIP4",
            "StructureChangeCode": "STATSTRU",
            "SubmissionYearOfPublicLibraryData": "YR_SUB",
            "TypeOfRegionServed": "GEOCODE",
        },
    }


@pytest.mark.integration
def test_repr():
    lib = PublicLibrariesSurvey(2017)

    assert str(lib) == "<PublicLibrariesSurvey 2017>"
