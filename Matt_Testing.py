import requests
from bs4 import BeautifulSoup

# 8-K test URL
# url = "https://www.sec.gov/Archives/edgar/data/354950/000035495017000017/hd_8kx05242017.htm"
# 10-K Test URLs
# url = "https://www.sec.gov/Archives/edgar/data/0001652044/000165204417000008/goog10-kq42016.htm"
# 10-Q URL
# url = "https://www.sec.gov/Archives/edgar/data/354950/000035495017000014/hd_10qx04302017.htm"
# 11-K Test URL
# url = "https://www.sec.gov/Archives/edgar/data/354950/000035495017000026/hd_prx11kx12312016.htm"
url = "https://www.sec.gov/Archives/edgar/data/936468/000119312517210489/d410677d11k.htm"


r = requests.get(url, stream=True)
soup = BeautifulSoup(r.content, 'lxml')


def CleanText(text):
    """Cleaning Text."""
    text = text.replace('\u200b', " ")
    text = text.replace('ý', '`check_marked`')
    text = text.replace('• \n', '')
    text = text.replace(u'\xa0', u'')
    text = text.replace(u'\x96', u'-')
    text = text.replace(u'\n', ' ')

    return text

cleanText = CleanText(str(soup))
soup = BeautifulSoup(cleanText, 'lxml')

# For finding number of pages and page locations


def Pages(text):
    """Finding Page Location by HR Tag."""
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
                        # print("Longer: " + str(pageBreak.find_previous_sibling('p').find_previous_sibling('p').text))
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
pageLoc = Pages(soup)


# Start of whats needed for Getting Table Of Contents

def GetTableOfContents(text):
    """Getting Table of Contents."""
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

TOC = GetTableOfContents(soup)

G_allSections = []


def MakeADict(lists):
    """Creating Dictionary of Table of Contents Sections and Pages."""
    newDict = {}
    for listy in lists:
        pageNum = 0
        myKey = []
        listy[:] = [item for item in listy if item != 'Table of Contents']
        for item in listy:
            try:
                if int(item):
                    pageNum = int(item)
                else:
                    pass
            except Exception:
                myKey.append(item)
        for section in myKey:
            newDict.update({str(section): pageNum})
            G_allSections.append(section)
    return newDict


G_TableOfContents = MakeADict(TOC)


class SecLocs(object):

    def __init__(self, SectionName):
        self.SectionName = SectionName
        self.StartPage = self.FindStartPage(SectionName)
        self.StartLoc = self.SectionPageBreaks(self.StartPage)
        self.NextSectionName = self.NextSectionName(SectionName)
        self.NextSectionStartPage = self.FindStartPage(self.NextSectionName)
        self.NextSectionStartLoc = self.SectionPageBreaks(self.NextSectionStartPage)
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


SectionName = G_allSections[2]

sl = SecLocs(SectionName)
print(sl.SectionName, sl.StartEndPages, sl.StartEndLocs, sl.NextSectionName)
