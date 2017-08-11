"""Crawl SEC Edgar DB and return filing information.

@author: Jake
"""
# -*- coding: utf-8 -*-

import requests
import pandas as pd
import re
import datetime
import time

class SecCrawler(object):
    #   Variables for SEC Edgar URL requests
    _SecBaseUrl = "https://www.sec.gov/cgi-bin/browse-edgar?"
    _SecArchivesUrl = 'https://www.sec.gov/Archives/edgar/data'
    _SecFilingParams = "&owner=exclude&action=getcompany"
    _headers = {"Connection": "close"}

    #   Variables for Date requests
    _Today = datetime.date.today()
    _20YearsAgo = (_Today - datetime.timedelta(days=365 * 20)).isoformat()
    _Today = _Today.isoformat()

    def __init__(self):
        pass

    def FindFiling(self, filing,
                   startDate=_20YearsAgo,
                   endDate=_Today,
                   ):

            #   Create filing url
            _FilingInfo = f"CIK={filing.ticker}&type={filing.FilingType}"
            SecFindFilingUrl = (self._SecBaseUrl + _FilingInfo +
                                self._SecFilingParams)

            #   Find and set Company CIK
            r = requests.get(SecFindFilingUrl)
            reg = re.search("(CIK=)\w+", r.text)
            CIK = (reg.group(0).strip("CIK="))
            filing.SetCIK(CIK)

            FilingsDF = pd.read_html(SecFindFilingUrl)[2]
            FilingsDF = self.CleanupFilingsDF(FilingsDF, startDate, endDate)
            n_FilingWanted = filing.Get_nFilingWanted()

            if len(FilingsDF.index) < n_FilingWanted:
                # TODO: need to log somewhere if n_filings are not available
                return None

            #   Find and set latest Acc No. of specified filing
            AccNum = re.search("(Acc-no: \d+-\d+-)\w+",
                               (FilingsDF["Description"][n_FilingWanted]))

            filing.SetAccNum(AccNum.group(0).strip("Acc-no: "))
            filing.SetFilingDate(FilingsDF["Filing Date"][n_FilingWanted])

            #   Set Filing and SGML Urls
            SecFilingUrl = (f"{self._SecArchivesUrl}/" +
                            f"{filing.CIK}/{filing.AccNumW_oDashes}/" +
                            f"{filing.AccNum}")

            #   Send requests and set Filing and SGML HEAD Text
            filingReq = requests.get(SecFilingUrl + ".txt",
                                     headers=self._headers, stream=True)
            SgmlHeadReq = requests.get(SecFilingUrl + ".hdr.sgml",
                                       headers=self._headers, stream=True)

            filing.SetFilingText(filingReq.text)
            filing.SetSgmlHead(SgmlHeadReq.text)

            G_filingListing.addFiling(filing)

    def CleanupFilingsDF(self, df, startDate, endDate):
        df.columns = df.iloc[0]
        df = df.reindex(df.index.drop(0))
        df = df[(df["Filing Date"] >= startDate) &
                (df["Filing Date"] <= endDate)]
        return df


class Filing(object):
    _working_FilingTypes = ['10-k', '8-k']

    def __init__(self, ticker, FilingType,
                 CIK=None, AccNum=None,
                 N_filingWanted=1, totalFilingsWanted=1):

        if FilingType not in self._working_FilingTypes:
            raise ValueError("Invalid filing type")
        else:
            self.ticker = ticker
            self.CIK = CIK
            self.FilingType = FilingType
            self.AccNum = AccNum
            self.N_filingWanted = N_filingWanted
            self.AccNumW_oDashes = None
            self.FilingText = None
            self.SgmlHead = None
            self.FilingDate = None
            self.totalFilingsWanted = totalFilingsWanted

    def GetTickAndType(self):
        return [self.ticker, self.FilingType]

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

    def Set_filingWanted(self, N_filingWanted):
        self.N_filingWanted = N_filingWanted

    def SetTotalFilingsWanted(self, totalFilingsWanted):
        self.totalFilingsWanted = totalFilingsWanted

    def Get_nFilingWanted(self):
        return self.N_filingWanted


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


G_filingListing = FilingList()


def SetInterimListing(Listing: list):
    from gevent.pool import Pool

    NUM_WORKERS = 4

    filingList = []

    for f in Listing:
        nIndex = f.totalFilingsWanted
        while nIndex > 0:
            filingList.append(
                Filing(*f.GetTickAndType(),
                       N_filingWanted=nIndex))
            nIndex -= 1

    pool = Pool(NUM_WORKERS)
    for f in filingList:
        pool.spawn(SecCrawler().FindFiling, f)
    start_time = time.time()
    pool.join()

    end_time = time.time()
    print(end_time - start_time)


def SetListingForTesting(Listing: list):
    filingList = []

    for f in Listing:
        nIndex = f.totalFilingsWanted
        while nIndex > 0:
            filingList.append(
                Filing(*f.GetTickAndType(),
                       N_filingWanted=nIndex))
            nIndex -= 1
    return filingList


def BaseTime():
    TestList = [Filing("goog", "8-k", totalFilingsWanted=15)]
    Listings = SetListingForTesting(TestList)

    start_time = time.time()
    [SecCrawler().FindFiling(f) for f in Listings]

    end_time = time.time()
    print(end_time - start_time)


if __name__ == "__main__":
    SetInterimListing([Filing("goog", "8-k", totalFilingsWanted=15)])
    BaseTime()
    print(len(G_filingListing))
