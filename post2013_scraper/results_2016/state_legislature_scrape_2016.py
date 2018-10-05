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
    url = 'https://ballotpedia.org/Alaska_House_of_Representatives_elections,_2016'
            
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
        
        # t = soup.find_all('table', {'class': 'bptable', 'style': 'align: center; border: 0px; background: white; text-align: center; box-shadow: 0px 2px 5px #A0A0A0; width: 100%;'})[0]

        df = pd.read_html(str(t))[0][1:]
        df.columns = df.iloc[0]
        df = df.drop(1)
        df = df.set_index(['District'])
        
        df['State'] = state
        df['Year'] = year
        df.columns.name=None
        
        df = df.loc[[keep_row(i) for i in df.index]]
                
        all_results = pd.concat([all_results, df], ignore_index=True)
        
    orig = all_results.copy()
    orig.head()
    all_results = orig.copy()
        
    def clean_name(x):
        x = x.replace(' (I)', '') # strip out incumbency indicator
        x = x.split(':')[0] # use everything before the colon
        return x
        
    for party in ['Democrat', 'Republican']:
        all_results[party + ' Incumbent'] = all_results[party].apply(lambda x: x.find('I') != -1)
        all_results[party + ' Votes'] = all_results[party].apply(lambda x: ''.join([i for i in x if i.isdigit()]))
        all_results[party] = all_results[party].apply(clean_name)
    
    all_results.head()
    
    # take care of vote totals when there is no candidate    
    no_rep = all_results['Republican'].apply(lambda x: x.startswith('No candidate'))
    no_dem = all_results['Democrat'].apply(lambda x: x.startswith('No candidate'))
    
    all_results.loc[no_dem, 'Democrat Votes'] = 0
    all_results.loc[no_rep, 'Republican Votes'] = 0
    
    
    all_results.loc[no_rep & (all_results['Democrat Votes']==''), 'Democrat Votes'] = 1
    all_results.loc[no_dem & (all_results['Republican Votes']==''), 'Republican Votes'] = 1
    
    
    # parse out votes and incumbency.
        
    all_results.to_csv('all_states.csv', encoding='utf-8')
    

if __name__ == '__main__':
    url_file = '2016_urls.csv'
    outfile = '2016_election_results.csv'
    race_results = scrape_results(url_file, outfile)
