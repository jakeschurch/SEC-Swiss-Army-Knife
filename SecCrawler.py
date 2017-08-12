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
    _SecCoParams = "&owner=exclude&action=getcompany"
    _headers = {"Connection": "close"}
    _TotalN_Requests = 0

    #   Variables for Date requests
    _Today = datetime.date.today()
    _20YearsAgo = _Today - datetime.timedelta(days=365 * 20)

    def __init__(self):
        pass

    def SetParamsForInitFiling(self, filing,
                               startDate=_20YearsAgo.isoformat(),
                               endDate=_Today.isoformat()):
        #   Create filing url
        _FilingParams = f"CIK={filing.ticker}&type={filing.FilingType}"
        _DateParams = f"&dateb={self._Today}&datea={self._20YearsAgo}"
        SecFindFilingUrl = (self._SecBaseUrl + _FilingParams + _DateParams +
                            self._SecCoParams)

        #   Find and set Company CIK
        r = self.GetRequest(SecFindFilingUrl, headers=self._headers,
                            stream=True)

        reg = re.search("(CIK=)\w+", r.text)
        CIK = (reg.group(0).strip("CIK="))
        filing.SetCIK(CIK)

        FilingsDF = pd.read_html(SecFindFilingUrl)[2]
        filing.SetFilingsDF(
            self.CleanupFilingsDF(FilingsDF)
        )

    def FindFiling(self, filing):

        if filing.AccNum is None: # loop control set by filing.FindAccNumAndFilingDate()
            return

        #   Set Filing and SGML Urls
        SecFilingUrl = (f"{self._SecArchivesUrl}/" +
                        f"{filing.CIK}/{filing.AccNumW_oDashes}/" +
                        f"{filing.AccNum}")

        #   Send requests and set Filing and SGML HEAD Text
        filingReq = self.GetRequest(SecFilingUrl + ".txt",
                                    headers=self._headers, stream=True)
        SgmlHeadReq = self.GetRequest(SecFilingUrl + ".hdr.sgml",
                                      headers=self._headers, stream=True)

        filing.SetFilingText(filingReq.text)
        filing.SetSgmlHead(SgmlHeadReq.text)

        G_filingListing.addFiling(filing)

    def CleanupFilingsDF(self, df):
        df.columns = df.iloc[0]
        df = df.reindex(df.index.drop(0))
        return df

    def GetRequest(self, URL, headers, stream):
        """Send URL request to SEC Edgar DB.

            Makes sure that we do not send more than 10 requests per second.
         """
        request = requests.get(URL, headers=headers, stream=stream)
        self._TotalN_Requests += 1
        if self._TotalN_Requests % 10 == 0:
            time.sleep(1)
        return request


class Filing(object):
    _working_FilingTypes = ['10-k', '8-k']

    def __init__(self, ticker, FilingType,
                 CIK=None, AccNum=None, FilingDate=None,
                 N_filingWanted=1, totalFilingsWanted=1, FilingsDF=None):

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
            self.FilingsDF = FilingsDF

    def GetInitKwargs(self, N_filingWanted):
        self.FindAccNumAndFilingDate(N_filingWanted)
        return {"ticker": self.ticker, "FilingType": self.FilingType,
                "CIK": self.CIK, "AccNum": self.AccNum,
                "FilingDate": self.FilingDate}

    def SetFilingsDF(self, df):
        self.FilingsDF = df

    def SetCIK(self, CIK):
        self.CIK = CIK

    def FindAccNumAndFilingDate(self, N_filingWanted):
        self.N_filingWanted = N_filingWanted

        if self.N_filingWanted > len(self.FilingsDF.index):
            AccNum = None
            # TODO: need to log somewhere if n_filings are not available
            return

        #   Find and set latest Acc No. of specified filing
        AccNum = re.search("(Acc-no: \d+-\d+-)\w+",
                           (self.FilingsDF["Description"][self.N_filingWanted])
                           )

        self.SetAccNum(AccNum.group(0).strip("Acc-no: "))
        self.SetFilingDate(self.FilingsDF["Filing Date"][self.N_filingWanted])


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
        SecCrawler().SetParamsForInitFiling(f)

        while nIndex > 0:
            filingList.append(
                Filing(
                    **f.GetInitKwargs(nIndex))
            )
            nIndex -= 1

    pool = Pool(NUM_WORKERS)
    for f in filingList:
        pool.spawn(SecCrawler().FindFiling, f)
    start_time = time.time()
    pool.join()

    end_time = time.time()
    print(f"Total run-time is: {end_time - start_time}")


def SetListingForTesting(Listing: list):
    raise Exception("Only for testing purposes")
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
    raise Exception("Only for testing purposes")
    TestList = [Filing("goog", "8-k", totalFilingsWanted=15)]
    Listings = SetListingForTesting(TestList)

    start_time = time.time()
    [SecCrawler().FindFiling(f) for f in Listings]

    end_time = time.time()
    print(end_time - start_time)


if __name__ == "__main__":
    SetInterimListing([Filing("goog", "8-k", totalFilingsWanted=2)])
    for f in G_filingListing:
        print(f.AccNum)
    # BaseTime()
    # print(len(G_filingListing))
