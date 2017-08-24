import requests
from bs4 import BeautifulSoup

# 8-K test URL
# url = "https://www.sec.gov/Archives/edgar/data/354950/000035495017000017/hd_8kx05242017.htm"
# 10-K Test URLs
url = "https://www.sec.gov/Archives/edgar/data/0001652044/000165204417000008/goog10-kq42016.htm"
# url = "https://www.sec.gov/Archives/edgar/data/936468/000119312517210489/d410677d11k.htm"
# 10-Q URL
# url = "https://www.sec.gov/Archives/edgar/data/354950/000035495017000014/hd_10qx04302017.htm"
# 11-K Test URL
# url = "https://www.sec.gov/Archives/edgar/data/354950/000035495017000026/hd_prx11kx12312016.htm"

r = requests.get(url, stream=True)
soup = BeautifulSoup(r.content, 'lxml')


def CleanText(text):
    """Cleaning Text."""
    text = text.replace('\u200b', " ")
    text = text.replace('ý', '`check_marked`')
    text = text.replace('• \n', '')
    text = text.replace(u'\xa0', u'')

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
                allText.append(a.text)

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

allSections = []


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
            allSections.append(section)
    return newDict


TableOfContents = MakeADict(TOC)
print(TableOfContents)


def FindStartPage(Section):
    """Finding Start Page of Given Section."""
    StartPage = TableOfContents.get(Section, "Section Does Not Exit")
    print(f'Page Number is {StartPage}')
    return StartPage


def SectionPageBreaks(SectionName):
    """Finding Location of Start Page of Given Section."""
    pageNum = FindStartPage(SectionName)
    HR_PassedTags = pageLoc.get(str(pageNum), "Not Found")
    print(f'Starting Position {HR_PassedTags} HR tags in')

SectionName = allSections[1]
# SectionName = "Risk Factors"

SectionPageBreaks(SectionName)
