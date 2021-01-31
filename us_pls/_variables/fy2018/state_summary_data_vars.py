from us_pls._variables.models import Variables

STATE_SUMMARY_DATA_VARIABLES = Variables(
    Identification=Variables(STABR="Name"),
    Population=Variables(
        POPU_LSA="Of_LegalServiceArea",
        F_POPLSA="F_POPLSA",
        POPU_UND="Of_LegalServiceAreas_Unduplicated",
        POPU_ST="Of_State_EstimateTotal",
    ),
    ServiceOutlets=Variables(
        CENTLIB="Num_CentralLibraries",
        F_CENLIB="F_CENLIB",
        BRANLIB="Num_BranchLibraries",
        F_BRLIB="F_BRLIB",
        BKMOB="Num_Bookmobiles",
        F_BKMOB="F_BKMOB",
    ),
    FullTimePaidStaff=Variables(
        MASTER="Total_Librarians_WithMasters",
        F_MASTER="F_MASTER",
        LIBRARIA="Total_Librarians",
        F_LIBRAR="F_LIBRAR",
        OTHPAID="Total_Other",
        F_OTHSTF="F_OTHSTF",
        TOTSTAFF="Total",
        F_TOTSTF="F_TOTSTF",
    ),
    OperatingRevenue=Variables(
        LOCGVT="From_LocalGovernment",
        F_LOCGVT="F_LOCGVT",
        STGVT="From_State",
        F_STGVT="F_STGVT",
        FEDGVT="From_FederalGovernment",
        F_FEDGVT="F_FEDGVT",
        OTHINCM="From_Other",
        F_OTHINC="F_OTHINC",
        TOTINCM="Total",
        F_TOTINC="F_TOTINC",
    ),
    OperatingExpenditures=Variables(
        Staff=Variables(
            SALARIES="Salaries",
            F_SALX="F_SALX",
            BENEFIT="EmployeeBenefits",
            F_BENX="F_BENX",
            STAFFEXP="Total",
            F_TOSTFX="F_TOSTFX",
        ),
        Collections=Variables(
            PRMATEXP="For_PrintMaterials",
            F_PRMATX="F_PRMATX",
            ELMATEXP="For_ElectonicMaterials",
            F_ELMATX="F_ELMATX",
            OTHMATEX="For_OtherMaterials",
            F_OTMATX="F_OTMATX",
            TOTEXPCO="Total",
            F_TOCOLX="F_TOCOLX",
        ),
        Other=Variables(OTHOPEXP="Total", F_OTHOPX="F_OTHOPX"),
        Total=Variables(TOTOPEXP="Total", F_TOTOPX="F_TOTOPX"),
    ),
    CapitalRevenue=Variables(
        LCAP_REV="From_LocalGovernment",
        F_LCAPRV="F_LCAPRV",
        SCAP_REV="From_State",
        F_SCAPRV="F_SCAPRV",
        FCAP_REV="From_FederalGovernment",
        F_FCAPRV="F_FCAPRV",
        OCAP_REV="Other",
        F_OCAPRV="F_OCAPRV",
        CAP_REV="Total",
        F_TCAPRV="F_TCAPRV",
    ),
    CapitalExpenditures=Variables(CAPITAL="Total", F_TCAPX="F_TCAPX"),
    LibraryCollections=Variables(
        BKVOL="Num_PrintMaterials",
        F_BKVOL="F_BKVOL",
        EBOOK="Num_EBooks",
        F_EBOOK="F_EBOOK",
        AUDIO_PH="Num_Audio_Physical",
        F_AUD_PH="F_AUD_PH",
        AUDIO_DL="Num_Audio_Downloadable",
        F_AUD_DL="F_AUD_DL",
        VIDEO_PH="Num_Video_Physical",
        F_VID_PH="F_VID_PH",
        VIDEO_DL="Num_Video_Downloadable",
        F_VID_DL="F_VID_DL",
    ),
    ElectronicCollections=Variables(
        EC_LO_OT="From_LocalOrOther",
        F_EC_L_O="F_EC_L_O",
        EC_ST="From_State",
        F_EC_ST="F_EC_ST",
        ELECCOLL="Total",
        F_ELECOL="F_ELECOL",
    ),
    OtherCollections=Variables(
        SUBSCRIP="CurrentPrintSerialSubscriptions", F_PRSUB="F_PRSUB"
    ),
    Hours=Variables(HRS_OPEN="Total", F_HRS_OP="F_HRS_OP"),
    Visits=Variables(
        VISITS="Total_Visits",
        F_VISITS="F_VISITS",
        REFERENC="Total_ReferenceTransactions",
        F_REFER="F_REFER",
        REGBOR="Total_RegisteredUsers",
        F_REGBOR="F_REGBOR",
    ),
    Circulation=Variables(
        TOTCIR="Total_Transactions",
        F_TOTCIR="F_TOTCIR",
        KIDCIRCL="Total_Transactions_ForChildrenMaterials",
        F_KIDCIR="F_KIDCIR",
        ELMATCIR="Total_Transactions_ForElectronicMaterials",
        F_EMTCIR="F_EMTCIR",
        PHYSCIR="Total_ForPhysicalItems",
        F_PHYSCR="F_PHYSCR",
        ELINFO="Total_ElectronicInfo_SuccessfulRetrieval",
        F_ELINFO="F_ELINFO",
        ELCONT="Total_ElectronicContentUse",
        F_ELCONT="F_ELCONT",
        TOTCOLL="Total",
        F_TOTCOL="F_TOTCOL",
    ),
    InterLibraryLoans=Variables(
        LOANTO="Total_LoansGiven",
        F_LOANTO="F_LOANTO",
        LOANFM="Total_LoansFrom",
        F_LOANFM="F_LOANFM",
    ),
    LibraryPrograms=Variables(
        TOTPRO="Total_Programs",
        F_TOTPRO="F_TOTPRO",
        KIDPRO="Total_Programs_ForChildren",
        F_KIDPRO="F_KIDPRO",
        YAPRO="Total_Programs_ForYoungAdults",
        F_YAPRO="F_YAPRO",
        TOTATTEN="Total_Attendance",
        F_TOTATT="F_TOTATT",
        KIDATTEN="Total_Attendance_ForChildren",
        F_KIDATT="F_KIDATT",
        YAATTEN="Total_Attendance_ForYoungAdults",
        F_YAATT="F_YAATT",
    ),
    OtherElectronicInfo=Variables(
        GPTERMS="Num_Computers",
        F_GPTERM="F_GPTERM",
        PITUSR="Num_ComputerUses",
        F_PITUSR="F_PITUSR",
        WIFISESS="Num_WiFiSessions",
        F_WIFISS="F_WIFISS",
        WEBVISIT="Num_VisitsToLibraryWebsite",
    ),
    Other=Variables(
        STARTDAT="ReportingPeriodStartDate",
        ENDDATE="ReportingPeriodEndDate",
        INCITSST="International CommitteeForInformationTechnologyStandardsStateCode_2Digit",
        YR_SUB="SubmissionYearOfPublicLibraryData",
        OBEREG="BureauOfEconomicsAnalysisCode",
    ),
)
