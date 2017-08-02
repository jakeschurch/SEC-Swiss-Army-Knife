# -*- coding: utf-8 -*-
"""
Created on Saturday June 10 17:58:50 2017

@author: Dave
"""
import time
import os
import errno
import requests
import re
from config import DEFAULT_DATA_PATH
import pandas as pd

t1 = time.time()

filing_type = '8-K'
sec_base_url = 'https://www.sec.gov/Archives/edgar/data'

try:
    print('Reading in company tickers, CIKs and file names')
    cdata=pd.read_csv('8k_company_list_4.01_2007-2016.csv')
except:
    print ("No input file Found")

cdata['SECFileName'] = cdata['FileName'].apply(lambda x: x[:-5])

retrieved_files = 0
sgml_retrieved_files = 0

for index, row in cdata.iterrows():
    #print (row['Ticker'], row['SECFileName'])
    
    # Set up all the required paths and URLs
    base_path = os.path.join(DEFAULT_DATA_PATH, filing_type, row['Ticker'])
    file_path = os.path.join(base_path,row['SECFileName'])
    a_code = re.sub(r"-", "", row['SECFileName'].split('.')[0])
    file_url = '/'.join([sec_base_url,str(row['CIK']),
                                 a_code,row['SECFileName']])
    sgml_hdr_filename = row['SECFileName'].split('.')[0]+'.hdr.sgml'
    sgml_hdr_url = '/'.join([sec_base_url,str(row['CIK']),
                                 a_code,sgml_hdr_filename])
    sgml_file_path = file_path.split('.')[0]+'hdr.sgml'
    
    # Retrieve and store SEC complete submission file if not already present
    if not os.path.exists(file_path):
        print ('Missing file for: ', row['Ticker'], row['SECFileName'])
        try:
            if not os.path.exists(base_path):
                try:
                    os.makedirs(base_path)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
            r = requests.get(file_url)
            with open(file_path, "w", encoding='utf-8') as f:
                f.write(r.text)  
            retrieved_files += 1
            print('Retrieved SEC file for: ', row['Ticker'], 
                  ' ', row['FilingDate'])
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    
    # Retrieve and store SEC SGML header for this filing if not already present           
    if not os.path.exists(sgml_file_path):
        print ('Missing SGML header file for: ',row['Ticker'],sgml_hdr_filename)
        try:
            if not os.path.exists(base_path):
                try:
                    os.makedirs(base_path)
                except OSError as exception:
                    if exception.errno != errno.EEXIST:
                        raise
            hdr = requests.get(sgml_hdr_url)
            with open(sgml_file_path, "w", encoding='utf-8') as f:
                f.write(hdr.text)  
            sgml_retrieved_files += 1
            print('Retrieved SGML header file for: ', row['Ticker'], 
                  ' ', row['FilingDate'])
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

t2 = time.time()                
print(retrieved_files, ' SEC complete submission files retrieved')
print(sgml_retrieved_files, ' SGML header files retrieved')
print("Total Time taken: ")
print(t2 - t1)    