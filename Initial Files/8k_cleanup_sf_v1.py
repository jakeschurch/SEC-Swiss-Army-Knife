# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 17:58:50 2017

@author: Dave
"""

import os
import errno
from bs4 import BeautifulSoup
#from config import DEFAULT_DATA_PATH
import pandas as pd
import re
#import binascii
#import html5lib
import sys

sys.setrecursionlimit(150)
DEFAULT_DATA_PATH = f"C:\\Users\student\\Desktop\\"

filing_type = '8-K'
text_suffixes = ['txt','htm','html']

try:
    print('Reading in company tickers, CIKs and file names')
    cdata=pd.read_csv('8k_company_list_4.01_2007-2016.csv')
except:
    print ("No input file Found")

cdata['SECFileName'] = cdata['FileName'].apply(lambda x: x[:-5])

# Initialize DocTypes column in cdata dataframe
cdata['DocTypes'] = ''

missing_files = 0
empty_files = 0

for index, row in cdata.iterrows():
    print (row['Ticker'], row['SECFileName'])
    # Diagnostic information
    ticker = row['Ticker']
    date = row['FilingDate']
    sec_filename = row['SECFileName']

    base_path = os.path.join(DEFAULT_DATA_PATH, filing_type, row['Ticker'])
    file_names = []
    doc_types = []
    raw_text = ''

    if os.path.exists(base_path):
        try:
            read_path = os.path.join(base_path,row['SECFileName'])
            if os.path.exists(read_path):
                with open(read_path, "r") as f:
                    data = f.read()
                soup = BeautifulSoup(data, "lxml")

                # Iterate through files packed in SEC complete submission file
                # saving text from those that are html or ascii
                for fname in soup.find_all('document'):
                    fn = fname.find('filename').contents[0].strip()
                    print(ticker, ' ', fn)
                    if fn not in file_names:
                        file_names.append(fn)
                        if fname.find('text'):
                            doc_body = fname.find('text')
                        else:
                            doc_body = ''
                        if fname.find('type'):
                            doc_type = fname.find('type').contents[0].strip()
                            doc_types.append(doc_type)
                        else:
                            doc_type = ''
                        #print(row['Ticker'], ' ', fn)
                        write_path = os.path.join(base_path,fn)

                        if fn.split('.')[-1] in text_suffixes:
                            raw_text += doc_body.get_text()
                        """
                            with open(write_path, "w", encoding='utf-8') as f:
                                f.write(doc_body.prettify(formatter='html')
                        else:
                            continue

                            with open(write_path, "wb") as f:
                                for line in doc_body.get_text().lstrip('\n'):
                                    f.write(binascii.a2b_uu(line))

                        """
                cdata.set_value(index,'DocTypes',[x for x in doc_types if x != 'GRAPHIC'])
                # Next, we deal with whitespace
                # Need to make this more efficient
                cleaned = re.sub(r"&nbsp;", " ", raw_text)
                cleaned = re.sub(r"\n", " ", cleaned)
                cleaned = re.sub(r"\t", " ", cleaned)
                cleaned = re.sub(r" +", " ", cleaned)
                #cleaned = re.sub(r"  ", " ", cleaned)
                if len(cleaned) > 0:
                    write_path = os.path.join(base_path,row['FileName'])
                    with open(write_path, "w", encoding='utf-8') as f:
                        f.write(cleaned)
                else:
                    empty_files += 1
                    print('Empty text string for filing: ', row['Ticker'],
                          ' ', row['FilingDate'])
            else:
                missing_files += 1
                print('Missing SEC file for: ', row['Ticker'],
                      ' ', row['FilingDate'])
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
                print(index, ' ', ticker, ' ', sec_filename)

cdata.to_csv('8k_doc_types_4.01_2007-2016.csv', header = True)

print(missing_files, ' SEC files missing')
print(empty_files, ' Empty files')
