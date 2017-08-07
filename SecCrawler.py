"""Crawl SEC Edgar DB and return filing information.

@author: Jake
"""
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import re
import datetime


class SecCrawler(object):
    #   Variables for SEC Edgar URL requests
    _SecBaseUrl = "https://www.sec.gov/cgi-bin/browse-edgar?"
    _SecArchivesUrl = 'https://www.sec.gov/Archives/edgar/data'
    _SecFilingParams = "&owner=exclude&action=getcompany"
    _headers = {"Connection": "close"}

    #   Variables for Date requests
    _Today = datetime.date.today()
    _OneYearAgo = (_Today - datetime.timedelta(days=365)).isoformat()
    _Today = _Today.isoformat()

    def __init__(self):
        pass

    def FindFiling(self, filingsList: list,
                   startDate=_OneYearAgo, endDate=_Today,
                   n_filings=1):

        for filing in filingsList:
            #   Create filing url
            _FilingInfo = f"CIK={filing.ticker}&type={filing.filing_type}"
            SecFindFilingUrl = (self._SecBaseUrl + _FilingInfo
                                + self._SecFilingParams)

            #   Find and set Company CIK
            r = requests.get(SecFindFilingUrl)
            reg = re.search("(CIK=)\w+", r.text)
            CIK = (reg.group(0).strip("CIK="))
            filing.SetCIK(CIK)

            FilingsDF = pd.read_html(SecFindFilingUrl)[2]
            FilingsDF = self.CleanupFilingsDF(FilingsDF, startDate, endDate)
            n_filings = self.nFilingsAvailable(FilingsDF, n_filings)

            for n in range(1, n_filings + 1):
                #   Find and set latest Acc No. of specified filing
                nFiling = Filing(filing.ticker, filing.filing_type)

                AccNum = re.search("(Acc-no: \d+-\d+-)\w+",
                                   (FilingsDF["Description"][n]))

                nFiling.SetAccNum(AccNum.group(0).strip("Acc-no: "))
                nFiling.SetFilingDate(FilingsDF["Filing Date"][n])

                #   Set Filing and SGML Urls
                AccNumW_oDashes = nFiling.AccNum.replace('-', "")
                SecFilingUrl = (f"{self._SecArchivesUrl}/" +
                                f"{filing.CIK}/{AccNumW_oDashes}/" +
                                f"{filing.AccNum}")

                #   Send requests and set Filing and SGML HEAD Text
                filingReq = requests.get(SecFilingUrl + ".txt",
                                         headers=self._headers, stream=True)
                SgmlHeadReq = requests.get(SecFilingUrl + ".hdr.sgml",
                                           headers=self._headers, stream=True)

                nFiling.SetFilingText(filingReq.text)
                nFiling.SetSgmlHead(SgmlHeadReq.text)

                global filingListing
                filingListing.append(nFiling)
                nFiling = None

    def CleanupFilingsDF(self, df, startDate, endDate):
        df.columns = df.iloc[0]
        df = df.reindex(df.index.drop(0))
        df = df[(df["Filing Date"] >= startDate) &
                (df["Filing Date"] <= endDate)]
        return df

    def nFilingsAvailable(self, df, n_FilingsWanted):
        # TODO: need to log somewhere if n_filings are not available
        if n_FilingsWanted <= len(df.index):
            return n_FilingsWanted
        else:
            return len(df.index)


class Filing(object):
    _working_filing_types = ['10-k', '8-k']

    def __init__(self, ticker, filing_type, CIK=None, AccNum=None):
        if filing_type not in self._working_filing_types:
            raise ValueError("Invalid filing type")
        else:
            self.ticker = ticker
            self.CIK = CIK
            self.filing_type = filing_type
            self.AccNum = AccNum
            self.FilingText = None
            self.SgmlHead = None
            self.FilingDate = None

    def SetCIK(self, CIK):
        self.CIK = CIK

    def SetAccNum(self, AccNum):
        self.AccNum = AccNum

    def SetFilingText(self, FilingText):
        self.FilingText = FilingText

    def SetSgmlHead(self, SgmlHead):
        self.SgmlHead = SgmlHead

    def SetFilingDate(self, FilingDate):
        self.FilingDate = FilingDate


if __name__ == "__main__":
    global filingListing
    filingListing = []

    googFiling = Filing("goog", "8-k")
    ibmFiling = Filing("ibm", "8-k")
    test = SecCrawler()
    test.FindFiling([googFiling, ibmFiling], startDate='2017-02-23', n_filings=10)

    for fil in filingListing:
        print(fil.ticker, fil.FilingDate)
