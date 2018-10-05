import pandas as pd
import requests
import re
import csv
from bs4 import BeautifulSoup as bs

def fetch_page(url):
    page = requests.get(url)
    return page.text

def pull_races(soup):
    #parse the BeautifulSoup input for races, return a list of races
    #the parsing is a mess, but I'll try to explain
    
    #find all districts
    df = pd.DataFrame()

    general = soup.find_all(text='November 8 General election candidates:')

    for idx, race in enumerate(general):
        candidates = race.find_parent('dd').findNextSiblings()

        district = 'District ' + str(idx+1)
    
        
        for cand in candidates:
            party = cand.find('a').get('title')
            
            text = cand.text
            
            if text.find('(I)') != -1:
                incumbent = True
            else:
                incumbent = False
            
            text = text.replace('(I) a', '')
                
            if text.find(':') != -1:
                name, vote = text.split(':')
            else:
                name = text
                if len(candidates) == 1:
                    vote = '1'
                else:
                    vote = '0'
                    
            name = name.strip()
            vote = ''.join([i for i in vote if i.isdigit()])
            
            df = df.append({'Name': name,
                       'Votes': vote,
                       'Party': party,
                       'Incumbent': incumbent,
                       'District': district},
                      ignore_index=True)
        
    return df



def read_urls(url_file):
    #parse the url file
    with open(url_file) as csvfile:
        reader = csv.reader(csvfile)
        urls = [(url[0],url[1],url[2]) for url in reader]
    return urls



def scrape_results(url_file, out_file):
    urls = read_urls(url_file)

    for year, state, url in urls:
        page_text = fetch_page(url)
        soup = bs(page_text, 'lxml')
        df = pull_races(soup)
            
        df['Year'] = year
        df['State'] = state
        
        df = df[['Year', 'State', 'District', 'Party', 'Name', 'Votes', 'Incumbent']]
        
        df.to_csv(out_file, index=False)
        
        
    

if __name__ == '__main__':
    url_file = '2016_url_ny.csv'
    out_file = '2016_election_results_ny.csv'
    
    scrape_results(url_file, out_file)