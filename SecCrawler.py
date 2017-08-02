# -*- coding: utf-8 -*-
"""
@author: Jake
"""
import requests
import pandas as pd
import re


class SecCrawler(object):
    _SecBaseUrl = "https://www.sec.gov/cgi-bin/browse-edgar?"
    _SecArchivesUrl = 'https://www.sec.gov/Archives/edgar/data'

    def __init__(self, ticker, filing_type):
        self.ticker = ticker
        self.filing_type = filing_type
        self.CIK = None
        self.AccNum = None

    def FindFiling(self):
        #   Create filing url
        _FilingInfo = f"CIK={self.ticker}&type={self.filing_type}"
        _SecFilingParams = "&owner=exclude&action=getcompany"
        SecFindFilingUrl = self._SecBaseUrl + _FilingInfo + _SecFilingParams

        #   Find and set Company CIK
        r = requests.get(SecFindFilingUrl)
        reg = re.search("(CIK=)\w+", r.text)
        CIK = (reg.group(0).strip("CIK="))
        self.SetCIK(CIK)

        #   Find and set latest Acc No. of specified filing
        AccNum = re.search("(Acc-no: \d+-\d+-)\w+",
                           (pd.read_html(SecFindFilingUrl)[2][2][1]))
        self.SetAccNum(AccNum.group(0).strip("Acc-no: "))

        #   Set Filing and SGML Urls
        AccNumW_oDashes = self.AccNum.replace('-', "")
        SecFilingUrl = (f"{self._SecArchivesUrl}/" +
                        f"{self.CIK}/{AccNumW_oDashes}/{self.AccNum}")
        filing = requests.get(SecFilingUrl + ".txt")
        sgml_head = requests.get(SecFilingUrl + ".hdr.sgml")
        print(filing.text, sgml_head.text)

    def Get10kFiling(self):
        assert NotImplementedError

    def Get8kFiling(self):
        assert NotImplementedError

    def Get13dFiling(self):
        assert NotImplementedError

    def SetCIK(self, CIK):
        self.CIK = CIK

    def SetAccNum(self, AccNum):
        self.AccNum = AccNum


if __name__ == "__main__":
    test = SecCrawler("goog", "8-k")
    test.FindFiling()
