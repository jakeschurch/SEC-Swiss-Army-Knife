# -*- coding: utf-8 -*-
__author__ = "Jake Schurch"

import SecCrawler as sc
import re
from bs4 import BeautifulSoup


def GetItemsFromSGML(SgmlHead):
    items = re.findall(r'(?:\<ITEMS\>)(\d{1}\.\d{2})', SgmlHead)
    return items


def CleanHtmlMarkup(markup: BeautifulSoup.find_all):
    markup = markup.replace('</font>', " </font>")
    markup = markup.replace("</div>", "\n</div>")
    markup = markup.replace("Table of Contents", "")

    return markup


def CleanTextMarkup(text: str):
    text = text.replace('\u200b', "")
    text = text.replace('• \n', '•')
    text = re.sub(r'[^\x00-\x7f]', r' ', text)
    text = re.sub(r'^\d+ $', r'', text, flags=re.MULTILINE)
    text = re.sub(r'\n\s+\n\s+\n\s+', '\n\n', text)

    return text


def GetCleanTags(HTML_Entity: BeautifulSoup.find):
    FoundTags = HTML_Entity.find_all(True, recursive=False)
    for _tag in FoundTags:
        if _tag.name == 'table':
            for descendant in _tag.descendants:
                try:
                    if ('style' in descendant.attrs and
                            'background-color' in descendant.attrs['style']):
                        _tag.clear()
                        _tag.decompose()
                        break
                except AttributeError:
                    pass

        elif (_tag.attrs is not None and
              'style' in _tag.attrs and
              'text-align:center' in _tag.attrs['style']):

            if _tag.string == '' or _tag.string is None:
                pass
            else:
                _tag.clear()
                _tag.decompose()

        elif _tag.name == 'hr':
            _tag.clear()
            _tag.decompose()

        else:
            pass

    return FoundTags


def FilingTextParser(filing: sc.Filing):
    _Content = BeautifulSoup(filing.FilingText, "lxml").find(['document',
                                                             'text'])
    _CleanTags = GetCleanTags(_Content)

    _CleanHtml = CleanHtmlMarkup(
        ''.join(str(_tag) for _tag in _CleanTags))

    CleanText = CleanTextMarkup(
        BeautifulSoup(_CleanHtml, 'lxml').text)

    with open('parseFilingTesting.txt', 'w+') as f:
        f.write(CleanText)

    return CleanText


if __name__ == "__main__":
    testListing = [sc.Filing("goog", "10-k", totalFilingsWanted=1)]
    sc.SetInterimListing(testListing)

    FilingTextParser(sc.G_filingListing[0])
