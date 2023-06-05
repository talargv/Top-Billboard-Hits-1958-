import re

import requests

from bs4 import BeautifulSoup
import pandas as pd


years = range(1958, 2024)
wiki_page_format = 'https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_top-ten_singles_in_{year}'


def get_one_year(year):
    link = wiki_page_format.format(year=str(year))
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    t = soup.find('table', class_='wikitable')


    rows = []
    current_span = 0
    date = ''
    for i in t.findAll('tr'):
        row = i.findAll('td')
        rows.append([])
        if current_span:
            rows[-1].append(date)
            current_span -= 1
        for n, j in enumerate(row):
            content = j.text.replace('\n', '')
            try:
                span = j.attrs['rowspan']
                if n == 0 and span.isdigit():
                    current_span = int(span) - 1
                    date = content
            except KeyError:
                pass
            rows[-1].append(content)
        if not rows[-1]:
            rows.pop()


    headers = [h.text for h in t.findAll('th')]
    num_columns = len(rows[0])
    headers = headers[:num_columns]
    # clean 
    for row in rows:
        for i,txt in enumerate(row):
            m = re.search('"[^"]+"',txt)
            if m:
                row[i] = m.group().replace('"','')

    data = pd.DataFrame(rows, columns=headers)
    year_column = pd.DataFrame([year]*len(rows), columns=[year])
    data.join(year_column)
    data.to_csv(f'hits_data_{year}.csv', index=False)



for y in years:
    get_one_year(y)