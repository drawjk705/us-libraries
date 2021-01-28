from enum import Enum


class DownloadType(Enum):
    Documentation = "Documentation.pdf"
    DataElementDefinitions = "DataElementDefinitions.pdf"
    CsvZip = "csvs.zip"


class DatafileType(Enum):
    SystemData = "SystemData.csv"
    StateSummaryAndCharacteristicData = "StateSummaryAndCharacteristicData.csv"
    OutletData = "OutletData.csv"
