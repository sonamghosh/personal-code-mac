from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
import requests
import csv
import pandas as pd
import errno
import sys
import os


class EdgarParser:
    def __init__(self, cik=None, ticker=None):
        if cik:
            self.cik = cik
        # Find CIK if given only the ticker and validate it
        else:
            self.ticker = ticker
            self.valid = ticker_validity_checker(self.ticker)
            if not self.valid:
                raise ValueError('This is not a valid ticker: ', self.ticker)
            self.cik = get_cik(self.ticker)

        # Required query links
        self.base_url = 'https://www.sec.gov'
        self.latest_form_url = '/cgi-bin/browse-edgar?action=getcompany&CIK='+str(self.cik)+'&type=13F'
        #self.prev_form_url = self.latest_form_url + '&dateb='

        # Start Session
        self.session = requests.Session()

    def ticker_validity_checker(self, ticker):
        # Open CSV file with mutual fund tickers into pandas dataframe
        data = pd.read_csv('mutual_fund_ticker_list.csv')
        # Check efficiently if ticker exists in the csv file
        valid = ticker in set(data.Ticker)
        if not valid:
            return False
        else:
            return True

    def get_cik(self, ticker):
        # Start HTML Session
        url = 'https://www.sec.gov/cgi-bin/series?ticker=' + \
               ticker+'&CIK=&sc=companyseries&type=N-PX&Find=Search'
        r = session.get(url)
        links = list(r.html.absolute_links)
        ticker_link = links[-3]  # 2nd last one contains CIK
        # Extract the CIK
        search_string = re.search('CIK=(.+?)&action', ticker_link)
        if search_string:
            found = search_string.group(1)

        return found

    def parse_recent_doc(self, cik):
        # Parses information from the most recent 13 F form

        # Query link
        url = urljoin(self.base_url, self.latest_form_url)

        # grab the most recent form
        parse_only = SoupStrainer('a', {'id': 'documentsbutton'})
        soup = BeautifulSoup(self.session.get(url).content, 'lxml',
                             parse_only=parse_only)
        recent_form_url = soup.find('a', {'id': 'documentsbutton'})['href']
        recent_form_url = urljoin(self.base_url, recent_form_url)

        # grab document url for the form
        parse_only = SoupStrainer('tr', {'class': 'blueRow'})
        soup = BeautifulSoup(self.session.get(recent_form_url).content, 'lxml',
                             parse_only=parse_only)
        form_url = soup.find_all('tr', {'class': 'blueRow'})[-1].find('a')['href']
        form_url = urljoin(self.base_url, form_url)

        return self.extract_information(form_url)

    def extract_information(self, url):
        # Extract Holdings information from 13-F document
        soup = BeautifulSoup(self.session.get(url).content, 'lxml')

        holdings = {h.text for h in soup.find_all((lambda tag: 'issuer' in tag.name.lower()))}
        if not holdings:
            print('No holdings at: {}'.format(url))
            return

        return holdings


# Testing
if __name__ == "__main__":
    print('Hello World')
    test = EdgarParser(cik='0001166559')
    a = test.parse_recent_doc(cik='0001166559')
    print(a)
    print(type(a))
