# -*- coding: utf-8 -*-
__author__ = "Jake Schurch"

import pickle
from collections import deque
import os


class Solenya(object):
    """Object serialized deque for filing lists."""
    DEFAULT_SETUP_PATH = fr"C:\Users\{os.getlogin()}\AppData\Roaming\Filings\.SecCrawler"

    def __init__(self, SetupPath=DEFAULT_SETUP_PATH,
                 fileName="serialized.pickle"):
        self.deque = deque(maxlen=5)
        self.DEFAULT_SETUP_PATH = SetupPath

        self.DEFAULT_FILE_PATH = (self.DEFAULT_SETUP_PATH +
                                  fr"\\{fileName.strip('.pickle')}" + '.pickle')

        if os.exists(self.DEFAULT_FILE_PATH) is False:
            os.makedirs(self.DEFAULT_FILE_PATH)

    # Methods for un/serializing deque
    def LoadPickledDeque(self):
        with open(fr"{self.DEFAULT_FILE_PATH}", 'rb') as handle:
            self.SetDeque(pickle.load(handle))

    def SavePickledDeque(self):
        with open(fr"{self.DEFAULT_FILE_PATH}", 'wb') as handle:
            pickle.dump(self.deque, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Deque Methods
    def GetDeque(self):
        return self.deque

    def SetDeque(self, newDeque):
        self.queue = newDeque

    def AddToDeque(self, newData):
        self.deque.append(newData)


if __name__ == '__main__':
    testing = Solenya("blah")
    # sc.SetInterimListing([sc.Filing("goog", "8-k", totalFilingsWanted=1)])

    testing.AddToDeque(1)
    testing.AddToDeque(2)
    testing.AddToDeque(3)
    testing.AddToDeque(4)
    testing.AddToDeque(5)
    testing.AddToDeque(6)
    testing.AddToDeque(7)
