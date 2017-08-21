"""Crawl SEC Edgar DB and return filing information."""
# -*- coding: utf-8 -*-
__author__ = "Jake Schurch"

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
                            stream=False)

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
                                    headers=self._headers, stream=False)
        SgmlHeadReq = self.GetRequest(SecFilingUrl + ".hdr.sgml",
                                      headers=self._headers, stream=False)

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
            time.sleep(0.5)
        return request


class Filing(object):
    _working_FilingTypes = ['10-k', '8-k']

    def __init__(self, ticker, FilingType,
                 CIK=None, AccNum=None, AccNumW_oDashes=None,
                 FilingDate=None, N_filingWanted=1,
                 totalFilingsWanted=1, FilingsDF=None):

        if FilingType not in self._working_FilingTypes:
            raise ValueError("Invalid filing type")
        else:
            self.ticker = ticker
            self.CIK = CIK
            self.FilingType = FilingType
            self.AccNum = AccNum
            self.AccNumW_oDashes = AccNumW_oDashes
            self.FilingDate = FilingDate
            self.N_filingWanted = N_filingWanted
            self.totalFilingsWanted = totalFilingsWanted
            self.FilingsDF = FilingsDF
            self.FilingText = None
            self.SgmlHead = None

    def GetInitKwargs(self, N_filingWanted):
        self.FindAccNumAndFilingDate(N_filingWanted)
        return {"ticker": self.ticker, "FilingType": self.FilingType,
                "CIK": self.CIK, "AccNum": self.AccNum,
                "AccNumW_oDashes": self.AccNumW_oDashes,
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


def SetInterimListing(
        Listing: list,
        startDate=SecCrawler._20YearsAgo.isoformat(),
        endDate=SecCrawler._Today.isoformat()):

    from gevent.pool import Pool

    NUM_WORKERS = 4

    filingList = []
    crawler = SecCrawler()
    for f in Listing:
        nIndex = f.totalFilingsWanted
        crawler.SetParamsForInitFiling(f, startDate=startDate, endDate=endDate)

        while nIndex > 0:
            filingList.append(
                Filing(**f.GetInitKwargs(nIndex))
            )
            nIndex -= 1

    pool = Pool(NUM_WORKERS)
    for f in filingList:
        pool.spawn(crawler.FindFiling, f)
    start_time = time.time()
    pool.join()

    end_time = time.time()
    print(f"Total run-time of SetInterimListing is: {end_time - start_time}")


if __name__ == "__main__":
    SetInterimListing([Filing("amzn", "8-k", totalFilingsWanted=1)])
