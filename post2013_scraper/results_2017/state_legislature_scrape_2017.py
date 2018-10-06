import re
import pandas as pd
import numpy as np
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import csv


class Candidate:

    def __init__(self, district, name, party, votes, winner, incumbent):
        self.district = district
        self.name = name
        self.party = party
        self.votes = votes
        self.winner = winner
        self.incumbent = incumbent

class Election:
    #holder for Candidate objects
    def __init__(self):
        self.candidates = []

    def add_candidate(self,new_candidate):
        self.candidates.append(new_candidate)


def party(x):
    if x.startswith('Write'):
        return x
    else:
        return (x + ' Party')


def extract_nj(url, state):
    state = 'New Jersey'
    election_list = []
                
    page_response = requests.get(url, timeout=5)
    page_content = bs(page_response.content, 'html.parser')
    
    N = 40
    districts = page_content.find_all('table', {'width': '500px'})[:N]
    
    for district in districts:
        election = Election()
        dnumber = district.find_all('th')[0].contents[0].contents[0]
        dnumber = re.search('District ([0-9]*)', dnumber).group(1)
        rows = district.find_all('tr')
        
        for r in rows[2:-2]: # loop over candidates
            if r.find('a', {'title': 'Won'}):
                winner = True
            else:
                winner = False
                
            if r.find(text='Incumbent'):
                incumbent = True
            else:
                incumbent = False
                                    
            for possible_name in r.find_all('a'):
                if possible_name.text == possible_name.get('title'):
                    name = possible_name.text
                    break

            partyname = r.find('td', {'width': '75px'}).contents[0].rstrip()
            vote = int(r.find_all('td')[-1].contents[0].replace(',', ''))
            # df = df.append({'District': dnumber, 'Party': party, 'Vote': vote}, ignore_index=True)
            cand = Candidate('District ' + dnumber, name, partyname, str(vote), winner, incumbent)
            
            election.add_candidate(cand)
        election_list.append(election)

    return election_list

def extract_va(url):
    state = 'Virginia'
    page_text = requests.get(url).text
    soup = bs(page_text, 'lxml')
    general = soup.find('span', {'id': 'General_election_candidates'})
    t = general.find_next('table')

    df = pd.read_html(str(t))[0][1:]

    df.columns = [i.replace('"', '').strip() for i in df.iloc[0]]
    df = df.drop(1)
    df = df.set_index(['District'])
        
    df['State'] = state
    df['Year'] = '2017'
    df.columns.name = None

    def keep_row(x):
        # keep row if it's not nan, not a weird character, and not Notes
        if x==x and not re.match('^\xc2', x) and not re.match('^Notes', x):
            return True
        else:
            return False

    df = df.loc[[keep_row(i) for i in df.index]]
            
    def clean_name(x):
        x = x.replace(' (I)', '') # strip out incumbency indicator
        x = x.split(':')[0] # use everything before the colon
        return x
        
    def find_vote_totals_by_party(x):
        # because some cells have multiple candidates, sum them
        votes = re.findall('(\d+)', x.replace(',', ''))
        votes = sum([int(i) for i in votes])
        return str(votes)

        
    for party in ['Democrat', 'Republican', 'Other']:
        index = ~df[party].isna()
        df.loc[index, party + ' Incumbent'] = df.loc[index, party].apply(lambda x: x.find('(I)') != -1)
        df.loc[index, party + ' Votes'] = df.loc[index, party].apply(find_vote_totals_by_party)
        df.loc[index, party] = df.loc[index, party].apply(clean_name)

    # take care of vote totals when there is no candidate    
    no_rep = df['Republican'].apply(lambda x: x.startswith('No candidate'))
    no_dem = df['Democrat'].apply(lambda x: x.startswith('No candidate'))
    
    df.loc[no_dem, 'Democrat Votes'] = 0
    df.loc[no_rep, 'Republican Votes'] = 0
    
    df.loc[no_rep & (df['Democrat Votes']==''), 'Democrat Votes'] = 1
    df.loc[no_dem & (df['Republican Votes']==''), 'Republican Votes'] = 1
    
    
    df['Other'] = df['Other'].fillna('No candidate')
    df[['Other Incumbent', 'Other Votes']] = df[['Other Incumbent', 'Other Votes']].fillna(0)
    
    
    return df



def write_results(race_results, outfile):
    #write the results to a CSV file
    with open(outfile,'w') as csvout:
        csvwriter = csv.writer(csvout)
        for year, state, results in race_results:
            for election in results:
                for candidate in election.candidates:
                    csvwriter.writerow([year, state,candidate.district, candidate.party, candidate.name, candidate.votes, candidate.winner, candidate.incumbent])

def scrape_results(file_nj, file_va):
    all_results = [('2017',
                    'New Jersey', 
                    extract_nj('https://ballotpedia.org/New_Jersey_General_Assembly_elections,_2017')
                    )
                   ]
    
    write_results(all_results, file_nj)
    
    va = extract_va('https://ballotpedia.org/Virginia_House_of_Delegates_elections,_2017')
    va.to_csv(file_va)
    


if __name__ == '__main__':
    scrape_results()
