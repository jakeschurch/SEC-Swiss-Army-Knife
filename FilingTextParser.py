# -*- coding: utf-8 -*-
import SecCrawler as sc
import re
from bs4 import BeautifulSoup
# TODO: remove page numbers, anything in a table, anything right aligned


def GetItemsFromSGML(SgmlHead):
    items = re.findall(r'(?:\<ITEMS\>)(\d{1}\.\d{2})', SgmlHead)
    return items

def FilingTextParser(filing):
    soup = BeautifulSoup(filing.FilingText, "lxml")
    content = soup.find(['document', 'text'])

    items = GetItemsFromSGML(filing.SgmlHead)
    print(items)
    cleanedHtml = CleanHtml(str(content))
    soup = BeautifulSoup(cleanedHtml, 'lxml')
    cleanedText = CleanText(soup.text)

    chosenOne = re.search(r'Item \d\.\d{2}\.[\s\S]+(?:Item \d\.\d{2}\.)', cleanedText, flags=re.MULTILINE)

    newTry = chosenOne.group(0)
    print(newTry)

    with open("parseFilingTesting.txt", 'w+') as f:
        # for char in cleanedText:
        #         try:
        #             f.write(char)
        #         except UnicodeEncodeError:
        #             pass
        f.write(newTry)


def CleanHtml(markup):
    markup = markup.replace('</font>', " </font>")
    markup = markup.replace("</div>", " </div>")

    return markup


def CleanText(text):
    text = text.replace('\u200b', " ")
    text = text.replace('ý', '`check_marked`')
    text = text.replace('• \n', '')

    return text


if __name__ == "__main__":
    # req = requests.get('https://www.sec.gov/Archives/edgar/data/1652044/000165204417000008/goog10-kq42016.htm')
    testListing = [sc.Filing("goog", "8-k", totalFilingsWanted=1)]
    sc.SetInterimListing(testListing)

    FilingTextParser(sc.G_filingListing[0])
