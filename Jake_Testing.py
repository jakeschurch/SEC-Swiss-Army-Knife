# -*- coding: utf-8 -*-
__author__ = "Jake Schurch"

import SecCrawler as sc
import re
import bs4
from bs4 import BeautifulSoup
import copy
from datetime import datetime


def CheckInputTypes(func):
    def wrapper(*args, **kwargs):

        for arg in args:
            ArgValue = next(iter(locals()['args']))
            ArgParamType = next(iter(func.__annotations__.keys()))

            if type(ArgValue) != func.__annotations__[ArgParamType]:
                raise TypeError(
                    "Arg: '{0}' in {1}() is not of type: {2}".format(
                        ArgParamType, func.__name__,
                        func.__annotations__[ArgParamType]))

        for kwarg in kwargs:
            if type(locals()['kwargs'][kwarg]) != func.__annotations__[kwarg]:
                raise TypeError(
                    "Kwarg: '{0}' in {1}() is not of type: {2}").format(
                        kwarg, func.__name__,
                        func.__annotations__[kwarg])
        return func(*args, **kwargs)
    return wrapper


@CheckInputTypes
def foo(bar: int, buz: int):
    int3 = bar + buz
    return int3


def GetItemsFromSGML(SgmlHead):
    items = re.findall(r'(?:\<ITEMS\>)(\d{1}\.\d{2})', SgmlHead)
    return items


def CleanHtmlMarkup(markup: bs4.element.ResultSet):
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


def GetCleanTags(HTML_Entity: bs4.element.ResultSet) -> list:

    FoundTags = HTML_Entity.find_all(True, recursive=False)
    for _tag in FoundTags:
        if _tag.name == 'table':
            for _descendant in _tag.descendants:
                try:
                    if ('style' in _descendant.attrs and
                            'background-color' in _descendant.attrs['style']):
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
            try:
                for _descendant in _tag.descendants:
                    try:
                        if ('style' in _descendant.attrs and 'background-color'
                                in _descendant.attrs['style']):
                            _descendant.clear()
                            _descendant.decompose()
                    except AttributeError:
                        pass
            except AttributeError:
                pass

    return FoundTags


def FilingTextParser(filing: sc.Filing):

    _Content = BeautifulSoup(filing.FilingText, "lxml").find(['document',
                                                             'text'])
    _CleanTags = GetCleanTags(HTML_Entity=_Content)

    _CleanHtml = CleanHtmlMarkup(
        ''.join(str(_tag) for _tag in _CleanTags))

    CleanText = CleanTextMarkup(
        BeautifulSoup(_CleanHtml, 'lxml').text)

    with open('parseFilingTesting.txt', 'w+') as f:
        f.write(CleanText)

    return CleanText


if __name__ == "__main__":

    sc.SetInterimListing([sc.Filing("goog", "10-k", totalFilingsWanted=1)])
    testFiling = sc.G_filingListing[0]
    FilingTextParser(testFiling)

    def func():
        pass

    '''d = globals().copy()

    print(datetime.datetime.now())

    for (item, val) in d.items():
        if type(d[item]) == type(func):
            globals()[item] = CheckInputTypes(d[item])

    foo(bar='hello', buz='world')'''
