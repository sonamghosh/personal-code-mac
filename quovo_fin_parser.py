import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import requests
import csv
import datetime
import logging
import sys
from bs4 import BeautifulSoup
import errno




def parse_doc(ticker=None, cik=None, prior_to=None, count=100):
    edgar_prefix = 'https://www.sec.gov/Archives/'
    if ticker == None and cik != None:
        # Add Find CIK function here
        print('babababa')
    elif ticker != None and cik == None:
        # Add Find Ticker function here
        print('Camels')
    elif ticker == None and cik == None:
        print('Bad boi')
    else:
        # Add Validity Checker uwu :3
        print('hello worldx')

    try:
        make_dir(cik, prior_to)
    except Exception as e:
        print(str(e))

    # generate url
    edgar_url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK='+str(cik)+'&type=13F&dateb='+\
                str(prior_to)+'&owner=exclude&output=xml&count='+str(count)

    print('Parsing 13-F' + str(ticker))
    r = requests.get(edgar_url)
    data = r.text

    print(data)
    doc_list, doc_name_list = create_document_list(data)

    print(doc_list)
    print(doc_name_list)

    try:
        save_to_dir(cik, prior_to, doc_list, doc_name_list)
    except Exception as e:
        print(str(e))

    print('Success')

def create_document_list(data):
    # parse data with beautiful soup
    soup = BeautifulSoup(data, features='lxml')
    # Store link in list
    link_list = list()

    # Convert .htm's to .html 
    for link in soup.find_all('filinghref'):
        url = link.string
        if link.string.split('.')[len(link.string.split('.'))-1] == 'htm':
            url += 'l'
        link_list.append(url)

    link_list_tot = link_list

    print('Number of files downloading {0}'.format(len(link_list_tot)))

    # List of url to the text documents
    doc_list = list()
    # List of doc names
    doc_name_list = list()

    # Get all the doc
    for i in range(len(link_list_tot)):
        required_url = link_list_tot[i].replace('-index.html', '')
        txtdoc = required_url + '.txt'
        docname = txtdoc.split("/")[-1]
        doc_list.append(txtdoc)
        doc_name_list.append(docname)

    return doc_list, doc_name_list

def get_url(url):
    if sys.version_info[0] >= 3:
        import urllib.request 
        content = urllib.request.urlopen(url).read()
    else:
        import urllib2
        content = urllib2.urlopen(url).read()

    return content



def make_dir(cik, prior_to):
    # Get current directory
    current_dir = os.getcwd()
    final_dir = os.path.join(current_dir, r'SEC-Edgar-Data')
    # Make dir to save company filings
    print('Path ==== ', path)
    
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
    


def save_to_dir(cik, prior_to, doc_list, doc_name_list):
    default_data_path = os.path.abspath(os.path.join(
                        os.path.dirname(__file__), '..', 'SEC-Edgar-Data'))
    # Save every text document into its respective folder
    for i in range(len(doc_list)):
        base_url = doc_list[i]
        r = requests.get(base_url)
        data = r.text
        path = os.path.join(default_data_path, cik, doc_name_list[i])

        with open(path, 'ab') as f:
            f.write(data.encode('ascii', 'ignore'))


if __name__ == "__main__":
    #parse_doc(ticker='AAPL', cik='0000320193')
    #parse_doc(ticker='BillBoi', cik='0001166559')
    make_dir('00023232', prior_to='20180509')
