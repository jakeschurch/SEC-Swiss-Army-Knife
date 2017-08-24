# -*- coding: utf-8 -*-
import SecCrawler as sc
import re
from bs4 import BeautifulSoup


def GetItemsFromSGML(SgmlHead):
    items = re.findall(r'(?:\<ITEMS\>)(\d{1}\.\d{2})', SgmlHead)
    return items


def FilingTextParser(filing):
    soup = BeautifulSoup(filing.FilingText, "lxml")
    content = soup.find(['document', 'text'])

    # with open('testHTML.txt', 'r') as f:
    #     text = f.read()
    #
    # soup = BeautifulSoup(text, 'lxml')

    findTags = content.find_all(True)

    for tag in findTags:
        if tag.name == 'table':
            for descendant in tag.descendants:
                try:
                    if ('style' in descendant.attrs) and ('background-color' in descendant.attrs['style']):
                        tag.decompose()
                        break
                except AttributeError:
                    pass
        elif tag.attrs is not None and 'style' in tag.attrs and 'text-align:center' in tag.attrs['style']:
            tag.decompose()
        elif tag.name == 'hr':
            tag.decompose()
        else:
            pass

    for tag in findTags:
        if tag.name == 'hr':
            print(True)

    notCenteredHTMLdoc = ''.join([str(tag) for tag in findTags])

    CleanedNotCenteredHTML = CleanHtml(notCenteredHTMLdoc)

    CleanedSoup = BeautifulSoup(CleanedNotCenteredHTML, 'lxml')

    CleanedText = CleanText(CleanedSoup.text)

    with open('parseFilingTesting.txt', 'w+') as f:
        f.write(CleanedText)


def CleanHtml(markup):
    markup = markup.replace('</font>', " </font>")
    markup = markup.replace("</div>", "\n</div>")
    markup = markup.replace("Table of Contents", "")

    return markup


def CleanText(text):
    text = text.replace('\u200b', "")
    text = text.replace('ý', '`check_marked`')
    text = text.replace('• \n', '•')
    text = re.sub(r'[^\x00-\x7f]', r' ', text)
    text = re.sub(r'^\d+ $', r'', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s+\n\s+\n\s+', '\n\n', text)

    return text


if __name__ == "__main__":
    # req = requests.get('https://www.sec.gov/Archives/edgar/data/1652044/000165204417000008/goog10-kq42016.htm')
    testListing = [sc.Filing("amzn", "10-k", totalFilingsWanted=1)]
    sc.SetInterimListing(testListing)

    FilingTextParser(sc.G_filingListing[0])
