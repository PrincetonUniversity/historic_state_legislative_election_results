from bs4 import BeautifulSoup as bs
import requests
import re
import csv
import pandas as pd

def fetch_page(url):
    page = requests.get(url)
    return page.text

def read_urls(url_file):
    #parse the URL file
    with open(url_file) as csvfile:
        reader = csv.reader(csvfile)
        urls = [(url[0],url[1],url[2]) for url in reader]
    return urls

def scrape_results(url_file, outfile):
    urls = read_urls(url_file)
    all_results = pd.DataFrame()
            
    def keep_row(x):
        # keep row if it's not nan, not a weird character, and not Notes
        if x==x and not re.match('^\xc2', x) and not re.match('^Notes', x):
            return True
        else:
            return False

    
    for year, state, url in urls:
        print(year, state)
        page_text = fetch_page(url)
        soup = bs(page_text, 'lxml')
        
        general = soup.find('span', {'id': 'General_election'})
        t = general.find_next('table')
        
        df = pd.read_html(str(t))[0][1:]
        df.columns = df.iloc[0]
        df = df.drop(1)
        
        df = df.set_index(['District'])
        
        df['State'] = state
        df['Year'] = year
        df.columns.name=None
        
        df = df.loc[[keep_row(i) for i in df.index]]
        
        df['District'] = df.index
                
        all_results = pd.concat([all_results, df], ignore_index=True)
        
    def clean_name(x):
        x = x.replace(' (I)', '') # strip out incumbency indicator
        x = x.split(':')[0] # use everything before the colon
        return x
        
    
    def find_vote_totals_by_party(x):
        # because some cells have multiple candidates, sum them
        votes = re.findall('(\d+)', x.replace(',', ''))
        if len(votes)==0:
            return ''
        else:
            votes = sum([int(i) for i in votes])
            return str(votes)

    
    for party in ['Democrat', 'Republican', 'Other']:
        index = ~all_results[party].isna()
        all_results.loc[index, party + ' Incumbent'] = all_results.loc[index, party].apply(lambda x: x.find('(I)') != -1)
        all_results.loc[index, party + ' Votes'] = all_results.loc[index, party].apply(find_vote_totals_by_party)
        all_results.loc[index, party] = all_results.loc[index, party].apply(clean_name)
                
    # take care of vote totals when there is no candidate    
    no_rep = all_results['Republican'].apply(lambda x: x.startswith('No candidate'))
    no_dem = all_results['Democrat'].apply(lambda x: x.startswith('No candidate'))
    
    all_results.loc[no_rep & no_dem * (all_results['Other Votes']==''), 'Other Votes'] = 1
    
    all_results.loc[no_dem, 'Democrat Votes'] = 0
    all_results.loc[no_rep, 'Republican Votes'] = 0
    
    all_results.loc[no_rep & (all_results['Democrat Votes']==''), 'Democrat Votes'] = 1
    all_results.loc[no_dem & (all_results['Republican Votes']==''), 'Republican Votes'] = 1
    
    all_results['Other'] = all_results['Other'].fillna('No candidate')
    all_results[['Other Incumbent', 'Other Votes']] = all_results[['Other Incumbent', 'Other Votes']].fillna(0)
        
    all_results.to_csv(outfile, encoding='utf-8')
    

if __name__ == '__main__':
    url_file = '2016_urls.csv'
    outfile = '2016_election_results.csv'
    race_results = scrape_results(url_file, outfile)
