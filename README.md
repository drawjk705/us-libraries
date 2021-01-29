# us-pls

A client to pull and query data from Public Libraries Survey.

<!--ts-->
   * [us-pls](#us-pls)
      * [The Public Libraries Survey](#the-public-libraries-survey)
      * [Getting started](#getting-started)
      * [Getting data](#getting-data)
      * [Understanding the variables](#understanding-the-variables)
         * ["But I don't want to read!"](#but-i-dont-want-to-read)

<!-- Added by: joel, at: Thu Jan 28 20:59:08 EST 2021 -->

<!--te-->

## The Public Libraries Survey

From the Institute of Museum and Library Services' [website](https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey):

The Public Libraries Survey (PLS) examines when, where, and how library services are changing to meet the needs of the public. These data, supplied annually by public libraries across the country, provide information that policymakers and practitioners can use to make informed decisions about the support and strategic management of libraries.

## Getting started

Begin by selecting the year of the survey:

```python
>>> from us_pls import PublicLibrariesSurvey
>>> pls_client = PublicLibrariesSurvey(year=2017)

<PublicLibrariesSurvey 2017>
```

## Getting data

The survey offers three datasets:

1. Public Library System Data File (`DatafileType.SystemData`). This contains one row per library in the US
2. Public Library State Summary/State Characteristics Data File (`DatafileType.StateSummaryAndCharacteristicData`). The contains one row per state in the US, as well as outlying areas.
3. Public Library Outlet Data File (`OutletData`). The contains data for public library service outlets (e.g., central, branch, bookmobile, and books-by-mail-only outlets)

To select and query a dataset, do the following:

```python
>>> from pls import DatafileType
>>> pls_client.get_stats(_for=DatafileType.<Type of interest>)

<pandas.DataFrame with the data>
```

## Understanding the variables

Unfortunately, the PLS does not have any API serving its data. As a result, this client works by scraping the PLS page (which contains all of its surveys), storing its survey and documentation URLs, and then downloading the surveys and documentation for the year of interest.

Because the documentation files are PDFs, and lack a standardized formatting from year to year, there is no deterministic way to extract variable data from them programmatically.

As a result, the client will also download a given year's survey's documentation. (By default it will store this in the your current directory under `data/<survey-year>/Documentation.pdf`.) So, if you want to verify what a variable name means, or, if you'd like to read more about that survey's methodology, that documentation file will be your friend.

### "But I don't want to read!"

If you really hate reading, or you want a broad overview of what each datafile contains, run the following (we're using the Outlet Data file as an example):

```python
>>> pls_client.read_docs(on=DatafileType.OutletData)

"Public Library Outlet Data File includes..."
```
