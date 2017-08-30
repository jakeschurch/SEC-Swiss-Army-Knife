import requests
from bs4 import BeautifulSoup

# TODO: rename Pages func
# TODO: rename Pages.mydict
# TODO: rename GetTableOfContents.piece
# TODO: make a funciton that puts everything through the 'pipeline'


def CleanText(text):
    """Cleaning Text."""
    text = text.replace('\u200b', " ")
    text = text.replace('ý', '`check_marked`')
    text = text.replace('• \n', '')
    text = text.replace(u'\xa0', u'')
    text = text.replace(u'\x96', u'-')
    text = text.replace(u'\n', ' ')

    return text


def Pages(text) -> dict:
    """Find Page Location by HR Tag."""
    PageNumToHR = []
    mydict = {}
    NumPages = 0
    HRTags = 0
    pageBreaks = text('hr')
    i = 0
    q = 0
    for pageBreak in pageBreaks:
        HRTags = HRTags + 1
        try:
            if pageBreak.previous_sibling.contents[0].text:
                # print(pageBreak.previous_sibling.contents[0].text)
                NumPages = NumPages + 1
                PageNumToHR.append([HRTags, NumPages])
                mydict.update({str(NumPages): str(HRTags)})
            else:
                pass
                q = q + 1
        except Exception:
            try:
                if int(pageBreak.find_previous_sibling('p').find_previous_sibling('p').text):
                    NumPages = NumPages + 1
                    PageNumToHR.append([HRTags, NumPages])
                    mydict.update({str(NumPages): str(HRTags)})
                else:
                    pass
                    q = q + 1
            except Exception:
                i = i + 1
                pass
    return mydict


def GetTableOfContents(text) -> list:
    """Get Table of Contents."""  # NOTE: Not needed after func name change, may want to change instead to output list
    tables = text('table')
    allText = []
    index = []
    i = 0
    d = 0
    for table in tables:
        if table.find('a'):
            for a in table.findAll('a'):
                tr = a.find_parent('tr')
                for string in tr.stripped_strings:
                    piece = string.split('-')
                    try:
                        if int(piece[0]) and int(piece[1]):
                            string = piece[0]
                    except Exception:
                        pass
                    allText.append(string)
    for phrase in allText:
        i = i + 1
        try:
            if int(phrase):
                numList = []
                numList.append(phrase)
                for num in range(d, i - 1):
                    numList.append(allText[num])
                d = i
                index.append(numList)
        except Exception:
            pass
    return index


def MakeTOC_Dict(listing: list) -> dict:
    """Creating Dictionary of Table of Contents Sections and Pages."""
    Toc_Dict = {}
    for l in listing:
        pageNum = 0
        myKey = []
        l[:] = [item for item in l if item != 'Table of Contents']
        for item in l:
            try:
                if int(item):
                    pageNum = int(item)
                else:
                    pass
            except Exception:
                myKey.append(item)
        for section in myKey:
            Toc_Dict.update({str(section): pageNum})
            G_allSections.append(section)
    return Toc_Dict


class Section(object):

    def __init__(self, SectionName: str, SectionStartPage: int):
        self.SectionName = SectionName
        self.SectionStartPage = SectionStartPage

    def GetSectionName(self):
        return self.SectionName


class TableOfContents(object):

    def __init__(self, ToC: dict) -> None:
        self.SectionList = []

        for SectionName, SectionStartPage in ToC.items():
            self.SectionList.append(
                Section(SectionName, SectionStartPage)
            )
        self._gen = self._YieldSection()

    def GetNextSection(self):
        return next(self._gen)

    def _YieldSection(self):
        for section in self.SectionList:
            yield section


class SecLocs(object):

    def __init__(self, SectionName):
        self.SectionName = SectionName
        self.StartPage = self.FindStartPage(SectionName)
        self.StartLoc = self.SectionPageBreaks(self.StartPage)
        self.NextSectionName = self.NextSectionName(SectionName)
        self.NextSectionStartPage = self.FindStartPage(self.NextSectionName)
        self.NextSectionStartLoc = self.SectionPageBreaks(
            self.NextSectionStartPage)
        self.StartEndPages = [self.StartPage, self.NextSectionStartPage]
        self.StartEndLocs = [self.StartLoc, self.NextSectionStartLoc]

    def FindStartPage(self, SectionName):
        """Finding Start Page of Given Section."""
        return G_TableOfContents.get(SectionName, "Section Does Not Exit")

    def SectionPageBreaks(self, StartPage):
        """Finding Location of Start Page of Given Section."""
        HR_PassedTags = pageLoc.get(str(StartPage), "Not Found")
        return int(HR_PassedTags)

    def NextSectionName(self, SectionName):
        """Findng Section Name of Next Section."""
        return G_allSections[G_allSections.index(SectionName) + 1]


def TestFilingText(typeWanted: str) -> str:
    """Get test url based on filing type."""
    #    url = "https://www.sec.gov/Archives/edgar/data/936468/000119312517210489/d410677d11k.htm"
    if typeWanted.lower() == '10-k':
        return "https://www.sec.gov/Archives/edgar/data/0001652044/000165204417000008/goog10-kq42016.htm"

    elif typeWanted.lower() == '10-q':
        return "https://www.sec.gov/Archives/edgar/data/354950/000035495017000014/hd_10qx04302017.htm"

    elif typeWanted.lower() == '11-k':
        return "https://www.sec.gov/Archives/edgar/data/354950/000035495017000026/hd_prx11kx12312016.htm"

    elif typeWanted.lower() == '8-k':
        return "https://www.sec.gov/Archives/edgar/data/354950/000035495017000017/hd_8kx05242017.htm"


# def Alt_TOC_Finder(url):
#     import pandas as pd
#
#     DF = pd.read_html(url)
#     for table in DF:
#         if table[0].str.contains('Item').any() and len(table.columns) > 1:
#             print(table.dropna())
#             return (table.dropna(thresh=2).reset_index(drop=True))


if __name__ == '__main__':

    url = TestFilingText('10-q')

    r = requests.get(url, stream=False)
    soup = BeautifulSoup(r.content, 'lxml')
    cleanText = CleanText(str(soup))
    soup = BeautifulSoup(cleanText, 'lxml')

    pageLoc = Pages(soup)

    TOC = GetTableOfContents(soup)

    G_allSections = []

    G_TableOfContents = MakeTOC_Dict(TOC)

    Testing = TableOfContents(G_TableOfContents)

    print(Testing.GetNextSection().GetSectionName())
    print(Testing.GetNextSection().GetSectionName())

    SectionName = G_allSections[2]

    sl = SecLocs(SectionName)
