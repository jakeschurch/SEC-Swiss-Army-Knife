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

    def FindFiling(self, filing, startDate=_OneYearAgo,
                   endDate=_Today, n_filings=1):
        #   Create filing url
        _FilingInfo = f"CIK={filing.ticker}&type={filing.filing_type}"
        SecFindFilingUrl = (self._SecBaseUrl + _FilingInfo
                            + self._SecFilingParams)

        #   Find and set Company CIK
        r = requests.get(SecFindFilingUrl)
        reg = re.search("(CIK=)\w+", r.text)
        CIK = (reg.group(0).strip("CIK="))
        filing.SetCIK(CIK)

        #   Find and set latest Acc No. of specified filing
        FilingsDF = pd.read_html(SecFindFilingUrl)[2]
        FilingsDF = self.CleanupFilingsDF(FilingsDF, startDate, endDate)
        print(FilingsDF["Description"])
        AccNum = re.search("(Acc-no: \d+-\d+-)\w+",
                           (FilingsDF["Description"][1]))

        filing.SetAccNum(AccNum.group(0).strip("Acc-no: "))

        #   Set Filing and SGML Urls
        AccNumW_oDashes = filing.AccNum.replace('-', "")
        SecFilingUrl = (f"{self._SecArchivesUrl}/" +
                        f"{filing.CIK}/{AccNumW_oDashes}/{filing.AccNum}")

        #   Send requests and set Filing and SGML HEAD Text
        filingReq = requests.get(SecFilingUrl + ".txt",
                                 headers=self._headers, stream=True)
        SgmlHeadReq = requests.get(SecFilingUrl + ".hdr.sgml",
                                   headers=self._headers, stream=True)

        filing.SetFilingText(filingReq.text)
        filing.SetSgmlHead(SgmlHeadReq.text)

    def CleanupFilingsDF(self, df, startDate, endDate):
        df.columns = df.iloc[0]
        df = df.reindex(df.index.drop(0))
        df = df[(df["Filing Date"] >= startDate) &
                (df["Filing Date"] <= endDate)]
        return df


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

    def SetCIK(self, CIK):
        self.CIK = CIK

    def SetAccNum(self, AccNum):
        self.AccNum = AccNum

    def SetFilingText(self, FilingText):
        self.FilingText = FilingText

    def SetSgmlHead(self, SgmlHead):
        self.SgmlHead = SgmlHead


if __name__ == "__main__":
    googFiling = Filing("goog", "8-k")

    test = SecCrawler()
    test.FindFiling(googFiling)
