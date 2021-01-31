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
            "CapitalExpenditures": {"CAPITAL": "Total", "F_TCAPX": "F_TCAPX"},
            "CapitalRevenue": {
                "CAP_REV": "Total",
                "FCAP_REV": "From_FederalGovernment",
                "F_FCAPRV": "F_FCAPRV",
                "F_LCAPRV": "F_LCAPRV",
                "F_OCAPRV": "F_OCAPRV",
                "F_SCAPRV": "F_SCAPRV",
                "F_TCAPRV": "F_TCAPRV",
                "LCAP_REV": "From_LocalGovernment",
                "OCAP_REV": "Other",
                "SCAP_REV": "From_State",
            },
            "Circulation": {
                "ELCONT": "Total_ElectronicContentUse",
                "ELINFO": "Total_ElectronicInfo_SuccessfulRetrieval",
                "ELMATCIR": "Total_Transactions_ForElectronicMaterials",
                "F_ELCONT": "F_ELCONT",
                "F_ELINFO": "F_ELINFO",
                "F_EMTCIR": "F_EMTCIR",
                "F_KIDCIR": "F_KIDCIR",
                "F_PHYSCR": "F_PHYSCR",
                "F_TOTCIR": "F_TOTCIR",
                "F_TOTCOL": "F_TOTCOL",
                "KIDCIRCL": "Total_Transactions_ForChildrenMaterials",
                "PHYSCIR": "Total_ForPhysicalItems",
                "TOTCIR": "Total_Transactions",
                "TOTCOLL": "Total",
            },
            "ElectronicCollections": {
                "EC_LO_OT": "From_LocalOrOther",
                "EC_ST": "From_State",
                "ELECCOLL": "Total",
                "F_EC_L_O": "F_EC_L_O",
                "F_EC_ST": "F_EC_ST",
                "F_ELECOL": "F_ELECOL",
            },
            "FullTimePaidStaff": {
                "F_LIBRAR": "F_LIBRAR",
                "F_MASTER": "F_MASTER",
                "F_OTHSTF": "F_OTHSTF",
                "F_TOTSTF": "F_TOTSTF",
                "LIBRARIA": "Total_Librarians",
                "MASTER": "Total_Librarians_WithMasters",
                "OTHPAID": "Total_Other",
                "TOTSTAFF": "Total",
            },
            "Hours": {"F_HRS_OP": "F_HRS_OP", "HRS_OPEN": "Total"},
            "Identification": {"STABR": "Name"},
            "InterLibraryLoans": {
                "F_LOANFM": "F_LOANFM",
                "F_LOANTO": "F_LOANTO",
                "LOANFM": "Total_LoansFrom",
                "LOANTO": "Total_LoansGiven",
            },
            "LibraryCollections": {
                "AUDIO_DL": "Num_Audio_Downloadable",
                "AUDIO_PH": "Num_Audio_Physical",
                "BKVOL": "Num_PrintMaterials",
                "EBOOK": "Num_EBooks",
                "F_AUD_DL": "F_AUD_DL",
                "F_AUD_PH": "F_AUD_PH",
                "F_BKVOL": "F_BKVOL",
                "F_EBOOK": "F_EBOOK",
                "F_VID_DL": "F_VID_DL",
                "F_VID_PH": "F_VID_PH",
                "VIDEO_DL": "Num_Video_Downloadable",
                "VIDEO_PH": "Num_Video_Physical",
            },
            "LibraryPrograms": {
                "F_KIDATT": "F_KIDATT",
                "F_KIDPRO": "F_KIDPRO",
                "F_TOTATT": "F_TOTATT",
                "F_TOTPRO": "F_TOTPRO",
                "F_YAATT": "F_YAATT",
                "F_YAPRO": "F_YAPRO",
                "KIDATTEN": "Total_Attendance_ForChildren",
                "KIDPRO": "Total_Programs_ForChildren",
                "TOTATTEN": "Total_Attendance",
                "TOTPRO": "Total_Programs",
                "YAATTEN": "Total_Attendance_ForYoungAdults",
                "YAPRO": "Total_Programs_ForYoungAdults",
            },
            "OperatingExpenditures": {
                "Collections": {
                    "ELMATEXP": "For_ElectonicMaterials",
                    "F_ELMATX": "F_ELMATX",
                    "F_OTMATX": "F_OTMATX",
                    "F_PRMATX": "F_PRMATX",
                    "F_TOCOLX": "F_TOCOLX",
                    "OTHMATEX": "For_OtherMaterials",
                    "PRMATEXP": "For_PrintMaterials",
                    "TOTEXPCO": "Total",
                },
                "Other": {"F_OTHOPX": "F_OTHOPX", "OTHOPEXP": "Total"},
                "Staff": {
                    "BENEFIT": "EmployeeBenefits",
                    "F_BENX": "F_BENX",
                    "F_SALX": "F_SALX",
                    "F_TOSTFX": "F_TOSTFX",
                    "SALARIES": "Salaries",
                    "STAFFEXP": "Total",
                },
                "Total": {"F_TOTOPX": "F_TOTOPX", "TOTOPEXP": "Total"},
            },
            "OperatingRevenue": {
                "FEDGVT": "From_FederalGovernment",
                "F_FEDGVT": "F_FEDGVT",
                "F_LOCGVT": "F_LOCGVT",
                "F_OTHINC": "F_OTHINC",
                "F_STGVT": "F_STGVT",
                "F_TOTINC": "F_TOTINC",
                "LOCGVT": "From_LocalGovernment",
                "OTHINCM": "From_Other",
                "STGVT": "From_State",
                "TOTINCM": "Total",
            },
            "Other": {
                "ENDDATE": "ReportingPeriodEndDate",
                "INCITSST": "International "
                "CommitteeForInformationTechnologyStandardsStateCode_2Digit",
                "OBEREG": "BureauOfEconomicsAnalysisCode",
                "STARTDAT": "ReportingPeriodStartDate",
                "YR_SUB": "SubmissionYearOfPublicLibraryData",
            },
            "OtherCollections": {
                "F_PRSUB": "F_PRSUB",
                "SUBSCRIP": "CurrentPrintSerialSubscriptions",
            },
            "OtherElectronicInfo": {
                "F_GPTERM": "F_GPTERM",
                "F_PITUSR": "F_PITUSR",
                "F_WIFISS": "F_WIFISS",
                "GPTERMS": "Num_Computers",
                "PITUSR": "Num_ComputerUses",
                "WEBVISIT": "Num_VisitsToLibraryWebsite",
                "WIFISESS": "Num_WiFiSessions",
            },
            "Population": {
                "F_POPLSA": "F_POPLSA",
                "POPU_LSA": "Of_LegalServiceArea",
                "POPU_ST": "Of_State_EstimateTotal",
                "POPU_UND": "Of_LegalServiceAreas_Unduplicated",
            },
            "ServiceOutlets": {
                "BKMOB": "Num_Bookmobiles",
                "BRANLIB": "Num_BranchLibraries",
                "CENTLIB": "Num_CentralLibraries",
                "F_BKMOB": "F_BKMOB",
                "F_BRLIB": "F_BRLIB",
                "F_CENLIB": "F_CENLIB",
            },
            "Visits": {
                "F_REFER": "F_REFER",
                "F_REGBOR": "F_REGBOR",
                "F_VISITS": "F_VISITS",
                "REFERENC": "Total_ReferenceTransactions",
                "REGBOR": "Total_RegisteredUsers",
                "VISITS": "Total_Visits",
            },
        }
    )
    assert lib.system_data_vars == Variables.from_dict(
        {
            "C_ADMIN": "AdministrativeStructureCode",
            "C_FSCS": "MeetsDefinitionOfPublicLibrary",
            "C_LEGBAS": "LegalBasisCode",
            "C_RELATN": "InterlibraryRelationshipCode",
            "CapitalExpenditures": {"CAPITAL": "Total", "F_TCAPX": "F_TCAPX"},
            "CapitalRevenue": {
                "CAP_REV": "Total",
                "FCAP_REV": "From_FederalGovernment",
                "F_FCAPRV": "F_FCAPRV",
                "F_LCAPRV": "F_LCAPRV",
                "F_OCAPRV": "F_OCAPRV",
                "F_SCAPRV": "F_SCAPRV",
                "F_TCAPRV": "F_TCAPRV",
                "LCAP_REV": "From_LocalGovernment",
                "OCAP_REV": "From_Other",
                "SCAP_REV": "From_StateGovernment",
            },
            "Circulation": {
                "ELCONT": "Total_ElectronicContentUse",
                "ELINFO": "Total_SuccessfulRetrievalOfElectronicInfo",
                "ELMATCIR": "Total_OfElectronicMaterials",
                "F_ELCONT": "F_ELCONT",
                "F_ELINFO": "F_ELINFO",
                "F_EMTCIR": "F_EMTCIR",
                "F_KIDCIR": "F_KIDCIR",
                "F_PHYSCR": "F_PHYSCR",
                "F_TOTCIR": "F_TOTCIR",
                "F_TOTCOL": "F_TOTCOL",
                "KIDCIRCL": "Total_OfChildrenMaterials",
                "PHYSCIR": "Total_OfPhysicalMaterials",
                "TOTCIR": "Total_Transactions",
                "TOTCOLL": "Total",
            },
            "ENDDATE": "ReportingPeriodEndDate",
            "ElectronicCollection": {
                "EC_LO_OT": "From_LocalOrOther",
                "EC_ST": "From_State",
                "ELECCOLL": "Total",
                "F_EC_L_O": "F_EC_L_O",
                "F_EC_ST": "F_EC_ST",
                "F_ELECOL": "F_ELECOL",
            },
            "FullTimePaidStaff": {
                "F_LIBRAR": "F_LIBRAR",
                "F_MASTER": "F_MASTER",
                "F_OTHSTF": "F_OTHSTF",
                "F_TOTSTF": "F_TOTSTF",
                "LIBRARIA": "Num_Employees_WithTitleLibrarian",
                "MASTER": "Num_PaidLibrarians_WithMasters",
                "OTHPAID": "Num_OtherPaidStaff",
                "TOTSTAFF": "Num_Total_PaidEmployees",
            },
            "GEOCODE": "TypeOfRegionServed",
            "Identification": {
                "FSCSKEY": "LibraryIdCode_FromIMLS",
                "LIBID": "LibraryIdCode_FromState",
                "LIBNAME": "Name",
                "STABR": "State",
            },
            "InterLibraryLoans": {
                "F_LOANFM": "F_LOANFM",
                "F_LOANTO": "F_LOANTO",
                "LOANFM": "Total_LoansReceived",
                "LOANTO": "Total_LoansGiven",
            },
            "LSABOUND": "DidLegalServiceAreaChanceInPastYear",
            "LibraryCollection": {
                "AUDIO_DL": "Num_AudioMaterials_Downloadable",
                "AUDIO_PH": "Num_AudioMaterials_Physical",
                "BKVOL": "Num_PrintMaterials",
                "EBOOK": "Num_ElectronicMaterials",
                "F_AUD_DL": "F_AUD_DL",
                "F_AUD_PH": "F_AUD_PH",
                "F_BKVOL": "F_BKVOL",
                "F_EBOOK": "F_EBOOK",
                "F_VID_DL": "F_VID_DL",
                "F_VID_PH": "F_VID_PH",
                "VIDEO_DL": "Num_VideoMaterials_Downloadable",
                "VIDEO_PH": "Num_VideoMaterials_Physical",
            },
            "LibraryPrograms": {
                "F_KIDATT": "F_KIDATT",
                "F_KIDPRO": "F_KIDPRO",
                "F_TOTATT": "F_TOTATT",
                "F_TOTPRO": "F_TOTPRO",
                "F_YAATT": "F_YAATT",
                "F_YAPRO": "F_YAPRO",
                "KIDATTEN": "Attendance_ForChildren_Total",
                "KIDPRO": "Total_ForChildren",
                "TOTATTEN": "Attendance_Total",
                "TOTPRO": "Total",
                "YAATTEN": "Attendance_ForYoungAdults_Total",
                "YAPRO": "Total_ForYoungAdults",
            },
            "LibraryServices": {
                "F_REFER": "F_REFER",
                "F_REGBOR": "F_REGBOR",
                "F_VISITS": "F_VISITS",
                "REFERENC": "Total_ReferenceTransactions",
                "REGBOR": "Total_RegisteredUsers",
                "VISITS": "Total_Visits",
            },
            "MailingAggress": {
                "ADDRES_M": "Address",
                "CITY_M": "City",
                "CNTY": "County",
                "PHONE": "PhoneNumber",
                "ZIP4_M": "ZipCode_4Digit",
                "ZIP_M": "ZipCode",
            },
            "OperatingExpenditures": {
                "Collection": {
                    "ELMATEXP": "ElectronicMaterials_Expenditures",
                    "F_ELMATX": "F_ELMATX",
                    "F_OTMATX": "F_OTMATX",
                    "F_PRMATX": "F_PRMATX",
                    "F_TOCOLX": "F_TOCOLX",
                    "OTHMATEX": "OtherMaterials_Expenditures",
                    "PRMATEXP": "PrintMaterials_Expenditures",
                    "TOTEXPCO": "Total_Expenditures",
                },
                "F_OTHOPX": "F_OTHOPX",
                "F_TOTOPX": "F_TOTOPX",
                "OTHOPEXP": "Other_Expenditures",
                "Staff": {
                    "BENEFIT": "EmployeeBenefits",
                    "F_BENX": "F_BENX",
                    "F_SALX": "F_SALX",
                    "F_TOSTFX": "F_TOSTFX",
                    "SALARIES": "Wages",
                    "STAFFEXP": "TotalExpenditures",
                },
                "TOTOPEXP": "TotalExpenditures",
            },
            "OperatingRevenue": {
                "FEDGVT": "Revenue_FromFederalGovernment",
                "F_FEDGVT": "F_FEDGVT",
                "F_LOCGVT": "F_LOCGVT",
                "F_OTHINC": "F_OTHINC",
                "F_STGVT": "F_STGVT",
                "F_TOTINC": "F_TOTINC",
                "LOCGVT": "Revenue_FromLocalGovernment",
                "OTHINCM": "Revenue_FromOtherSources",
                "STGVT": "Revenue_FromStateGovernment",
                "TOTINCM": "Revenue_Total",
            },
            "Other": {
                "CBSA": "CoreBasedStatisticalArea",
                "CDCODE": "CongressionalDistrict",
                "CENBLOCK": "CensusBlock",
                "CENTRACT": "CensusTract",
                "CNTYPOP": "CountyPopulation",
                "ENDDATE": "ReportingPeriodEndDate",
                "GEOMATCH": "Geocoding_AccuraryAndPrecision",
                "GNISPLAC": "GeographicNamesInformationSystemFeatureId",
                "INCITSCO": "InternationalCommitteeForInfoTechStandardsStateCode_3Digit",
                "INCITSST": "InternationalCommitteeForInfoTechStandardsStateCode_2Digit",
                "LATITUDE": "Latitude",
                "LOCALE_ADD": "CategorizationOfLocale_BySizeAndProximityToCities",
                "LOCALE_MOD": "CategorizationOfLocale_ByModalLocaleCodeOfAssociatedStationaryOutlets",
                "LONGITUD": "Longitute",
                "MICROF": "MetropolitanAndMicropolitcanStatisticalAreaFlag",
                "OBEREG": "BureauOfEconomicAnalysisCode",
                "REAPLOCALE_ADD": "CategorizationOfLocale_BySizeAndProximityToCities_FromRuralEducationAchievementProgram",
                "REAPLOCALE_MOD": "CategorizationOfLocale_ByModalLocaleCodeOfAssociatedStationaryOutlets_FromRuralEducationAchievementProgram",
                "RSTATUS": "ReportingStatus",
                "STARTDAT": "ReportingPeriodStartDate",
                "STATADDR": "AddressChangeCode",
                "STATNAME": "NameChangeCode",
                "STATSTRU": "StructureChangeCode",
                "YR_SUB": "SubmissionYearOfPublicLibraryData",
            },
            "OtherElectronicInformation": {
                "F_GPTERM": "F_GPTERM",
                "F_PITUSR": "F_PITUSR",
                "F_WIFISS": "F_WIFISS",
                "GPTERMS": "Num_ComputersUsedByPublic",
                "PITUSR": "Num_UsagesOfComputers",
                "WEBVISIT": "Num_VisitsToLibraryWebsite",
                "WIFISESS": "Num_WiFiUses",
            },
            "Population": {
                "F_POPLSA": "F_POPLSA",
                "POPU_LSA": "Of_LegalServiceArea",
                "POPU_UND": "Of_LegalServiceArea_Unduplicated",
            },
            "PrintSerialSubscriptions": {"F_PRSUB": "F_PRSUB", "SUBSCRIP": "Total"},
            "PublicServiceHours": {
                "F_HRS_OP": "F_HRS_OP",
                "HRS_OPEN": "Total_HoursOpen_PerYear",
            },
            "STARTDAT": "ReportingPeriodStartDate",
            "ServiceOutlets": {
                "BKMOB": "Num_Bookmobiles",
                "BRANLIB": "Num_BranchLibraries",
                "CENTLIB": "Num_CentralLibraries",
                "F_BKMOB": "F_BKMOB",
                "F_BRLIB": "F_BRLIB",
                "F_CENLIB": "F_CENLIB",
            },
            "StreetAddress": {
                "ADDRESS": "Address",
                "CITY": "City",
                "ZIP": "ZipCode",
                "ZIP4": "ZipCode_4Digit",
            },
        }
    )
    assert lib.outlet_data_vars == Variables.from_dict(
        {
            "CBSA": "CoreBasedStatisticalArea",
            "CDCODE": "CongressionalDistrict",
            "CENBLOCK": "CensusBlock",
            "CENTRACT": "CensusTract",
            "CNTYPOP": "CountyPopulation",
            "C_OUT_TY": "OutletType",
            "F_SQ_FT": "F_SQ_FT",
            "GEOMATCH": "Geocoding_AccuracyAndPrecision",
            "GNISPLAC": "GeographicNamesInformationSystemFeatureId",
            "HOURS": "HoursOpen",
            "INCITSCO": "InternationalCommiteeForInfoTechStandardsStateCode_ThreeDigit",
            "INCITSST": "InternationalCommiteeForInfoTechStandardsStateCode_TwoDigit",
            "Identification": {
                "ADDRESS": "Address",
                "CITY": "City",
                "CNTY": "County",
                "C_FSCS": "MeetsDefinitionOfPublicLibrary",
                "FSCSKEY": "LibraryIdCode_FromIMLS",
                "FSCS_SEQ": "LibraryIdCode_Suffix",
                "LIBID": "LibraryIdCode_FromState",
                "LIBNAME": "Name",
                "PHONE": "Phone",
                "STABR": "State",
                "ZIP": "ZipCode",
                "ZIP4": "ZipCode_4Digit",
            },
            "LATITUDE": "Latitude",
            "LOCALE": "CategorizationOfLocale_BySizeAndProximityToCities",
            "LONGITUD": "Longitude",
            "L_NUM_BM": "Num_BookmobilesInBookmobileOutletRecord",
            "MICROF": "MetropolitanAndMicropolitcanStatisticalAreaFlag",
            "OBEREG": "BureauOfEconomicsAnalysisCode",
            "REAPLOCALE": "CategorizationOfLocale_BySizeAndProximityToCities_FromRuralEducationAchievementProgram",
            "SQ_FEET": "SquareFootage",
            "STATADDR": "AddressChangeCode",
            "STATNAME": "NameChangeCode",
            "STATSTRU": "StructureChangeCode",
            "WKS_OPEN": "WeeksOpen",
            "YR_SUB": "SubmissionYearOfPublicLibraryData",
        }
    )


@pytest.mark.integration
def test_repr():
    lib = PublicLibrariesSurvey(2017)

    assert str(lib) == "<PublicLibrariesSurvey 2017>"
