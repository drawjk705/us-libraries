from enum import Enum


class DownloadType(Enum):
    Documentation = "Documentation.pdf"
    DataElementDefinitions = "DataElementDefinitions.pdf"

    # unzipped CSV files
    CsvZip = "csvs.zip"
    SystemDataFile = "SystemDataFile.csv"
    StateSummaryAndCharacteristicData = "StateSummaryAndCharacteristicData.csv"
    OutletData = "OutletData.csv"