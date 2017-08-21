"""Store and manage filings in specified folders."""
# -*- coding: utf-8 -*-
__author__ = "Jake Schurch"

import os
import SecCrawler as sc


class FilingManager(object):
    DEFAULT_DATA_PATH = fr"C:\Users\{os.getlogin()}\Desktop\Filings"

    def __init__(self, **kwargs):
        if os.name != "nt":
            raise Exception("Non-Windows Operating Systems " +
                            "are currently not supported!")
        if 'DEFAULT_DATA_PATH' in kwargs:
            self.DEFAULT_DATA_PATH = kwargs['DEFAULT_DATA_PATH']

    #   Directory Methods
    def MakeDir(self, DirName):
        if self.CheckDirExists(DirName) is False:
            os.makedirs(DirName)
        else:
            raise FileExistsError

    def RemoveDir(self, DirName):
        if self.CheckDirExists(DirName):
            os.rmdir(DirName)
        else:
            raise FileExistsError

    def CheckDirExists(self, DirName):
        if os.path.exists(DirName):
            return True
        else:
            return False

    def CheckMakeAndSetDir(self, DirName):
        if self.CheckDirExists(DirName) is False:
            self.MakeDir(DirName)
        os.chdir(DirName)

    #   Filing Methods
    def SaveFilingsInDir(self, FilingsListing: list):
        if self.CheckDirExists(self.DEFAULT_DATA_PATH) is False:
            self.MakeDir(self.DEFAULT_DATA_PATH)

        if self.CheckDirExists(self.DEFAULT_SETUP_PATH) is False:
            self.MakeDir(self.DEFAULT_SETUP_PATH)

        for filing in FilingsListing:
            os.chdir(self.DEFAULT_DATA_PATH)

            #   Does Ticker dir exist?
            tickerPath = os.path.join(self.DEFAULT_DATA_PATH + "\\" +
                                      filing.ticker)
            self.CheckMakeAndSetDir(tickerPath)

            #   Does Ticker\filingType dir exist?
            filingTypePath = os.path.join(tickerPath + "\\" +
                                          filing.FilingType)
            self.CheckMakeAndSetDir(filingTypePath)

            #   Does Ticker\filingType\AccNum dir exist?
            AccNumPath = os.path.join(filingTypePath + "\\" + filing.AccNum)
            self.CheckMakeAndSetDir(AccNumPath)

            #   Save Filing text in files
            with open(f"{filing.AccNumW_oDashes}.txt", "w+") as f:
                f.write(filing.FilingText)

            with open(f"{filing.AccNumW_oDashes}.hdr.sgml", "w+") as f:
                f.write(filing.SgmlHead)

    def OpenFiling(self, filing):
        os.startfile(filing)


def TestingFilingManger():
    testListing = [sc.Filing("goog", "8-k", totalFilingsWanted=5)]
    sc.SetInterimListing(testListing)

    foo = FilingManager()
    foo.SaveFilingsInDir(sc.G_filingListing)


if __name__ == "__main__":
    TestingFilingManger()
    #   os.startfile("testfile.txt")
