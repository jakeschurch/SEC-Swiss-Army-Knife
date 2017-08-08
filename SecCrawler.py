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
            _FilingInfo = f"CIK={filing.ticker}&type={filing.FilingType}"
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
                nFiling = Filing(filing.ticker, filing.FilingType, filing.CIK)

                AccNum = re.search("(Acc-no: \d+-\d+-)\w+",
                                   (FilingsDF["Description"][n]))

                nFiling.SetAccNum(AccNum.group(0).strip("Acc-no: "))
                nFiling.SetFilingDate(FilingsDF["Filing Date"][n])

                #   Set Filing and SGML Urls
                SecFilingUrl = (f"{self._SecArchivesUrl}/" +
                                f"{nFiling.CIK}/{nFiling.AccNumW_oDashes}/" +
                                f"{nFiling.AccNum}")

                #   Send requests and set Filing and SGML HEAD Text
                filingReq = requests.get(SecFilingUrl + ".txt",
                                         headers=self._headers, stream=True)
                SgmlHeadReq = requests.get(SecFilingUrl + ".hdr.sgml",
                                           headers=self._headers, stream=True)

                nFiling.SetFilingText(filingReq.text)
                nFiling.SetSgmlHead(SgmlHeadReq.text)

                filingListing.addFiling(nFiling)

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
    _working_FilingTypes = ['10-k', '8-k']

    def __init__(self, ticker, FilingType, CIK=None, AccNum=None):
        if FilingType not in self._working_FilingTypes:
            raise ValueError("Invalid filing type")
        else:
            self.ticker = ticker
            self.CIK = CIK
            self.FilingType = FilingType
            self.AccNum = AccNum
            self.AccNumW_oDashes = None
            self.FilingText = None
            self.SgmlHead = None
            self.FilingDate = None

    def SetCIK(self, CIK):
        self.CIK = CIK

    def SetAccNum(self, AccNum):
        self.AccNum = AccNum
        self.AccNumW_oDashes = AccNum.replace('-', "")

    def SetFilingText(self, FilingText):
        self.FilingText = FilingText

    def SetSgmlHead(self, SgmlHead):
        self.SgmlHead = SgmlHead

    def SetFilingDate(self, FilingDate):
        self.FilingDate = FilingDate


class FilingList(list):
    def __init__(self):
        pass

    def addFiling(self, filing: Filing):
        if isinstance(filing, Filing) is False:
            raise Exception("filing is not of type: " +
                            f"<class '{__name__}.Filing'>" +
                            f"but of type: {(type(filing))}")
        else:
            self.append(filing)

    def GetFilingList(self):
        return self


filingListing = FilingList()

if __name__ == "__main__":
    '''global filingListing
    filingListing = []


    ibmFiling = Filing("ibm", "8-k")


    print(newL.GetFilingList())'''
    googFiling = Filing("goog", "8-k")

    test = SecCrawler()
    test.FindFiling([googFiling])
    for filing in filingListing:
        print(filing.FilingText)
