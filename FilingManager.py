r"""Store and manage filings in specified folders.

@author: Jake

Potential path structure: ~\Filings\Ticker\FilingType\AccNum
"""
# -*- coding: utf-8 -*-

import os


class FilingManager(object):
    _user = os.getlogin()
    DEFAULT_DATA_PATH = fr"C:\Users\{_user}\Desktop"

    def __init__(self, **kwargs):
        if 'DEFAULT_DATA_PATH' in kwargs:
            self.DEFAULT_DATA_PATH = kwargs['DEFAULT_DATA_PATH']

    #   Directory Methods
    def MakeDir(self, DirName):
        raise NotImplementedError

    def RemoveDir(self, DirName):
        raise NotImplementedError

    #   Filing Methods
    def SaveFilingsInDir(self, FilingsListing: list):
        raise NotImplementedError


if __name__ == "__main__":
    foo = FilingManager()
    print(foo.DEFAULT_DATA_PATH)
