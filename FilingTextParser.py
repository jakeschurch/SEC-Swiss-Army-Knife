# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
# TODO: remove page numbers, anything in a table, anything right aligned


def FilingTextParser(markup, encoding):
    soup = BeautifulSoup(markup, "lxml", from_encoding=encoding)
    content = soup.find(['document', 'text'])

    cleanedHtml = CleanHtml(str(content))
    soup = BeautifulSoup(cleanedHtml, 'lxml')
    cleanedText = CleanText(soup.text)
    with open("parseFilingTesting.txt", 'w+') as f:
        f.write(cleanedText)


def CleanHtml(markup):
    markup = markup.replace('</font>', " \n</font>")
    markup = markup.replace("</div>", " \n</div>")

    return markup


def CleanText(text):
    text = text.replace('\u200b', " ")
    text = text.replace('ý', '`check_marked`')
    text = text.replace('• \n', '')

    return text


if __name__ == "__main__":
    req = requests.get('https://www.sec.gov/Archives/edgar/data/1652044/000165204417000008/goog10-kq42016.htm')
    FilingTextParser(req.text, req.encoding)
