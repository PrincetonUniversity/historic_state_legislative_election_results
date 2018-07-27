import re
import pandas as pd
import numpy as np
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import csv


class Candidate:

    def __init__(self, district, name, party, votes, winner):
        self.district = district
        self.name = name
        self.party = party
        self.votes = votes
        self.winner = winner

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


def extract_race_results(url, state):
    election_list = []
    
    if state=='Virginia':
        df = pd.read_json(url)

        for _, race in df.iterrows():
            election = Election()

            races = race['Races']
            raceno = re.search('\((.*)\)', # capture characters within parentheses
                               races['RaceName']).group(1).lstrip('0')

            votes = [cand['Votes'] for cand in races['Candidates']]
            winner = np.argmax(votes)

            for i, cand in enumerate(races['Candidates']):
                if i != winner:
                    cand['Winner'] = False
                else:
                    cand['Winner'] = True

            for cand in races['Candidates']:
                cand = Candidate('District ' + raceno, cand['BallotName'], party(cand['PoliticalParty']), str(cand['Votes']), cand['Winner'])
                cand
                election.add_candidate(cand)

            election_list.append(election)
            
    elif state=='New Jersey':
        page_response = requests.get('https://ballotpedia.org/New_Jersey_General_Assembly_elections,_2017', timeout=5)
        page_content = bs(page_response.content, 'html.parser')
        
        N = 40
        districts = page_content.find_all('table', {'width': '500px'})[:N]
        district = districts[0]
        # df = pd.DataFrame()
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
                                        
                for possible_name in r.find_all('a'):
                    if possible_name.text == possible_name.get('title'):
                        name = possible_name.text
                        break

                partyname = r.find('td', {'width': '75px'}).contents[0].rstrip()
                vote = int(r.find_all('td')[-1].contents[0].replace(',', ''))
                # df = df.append({'District': dnumber, 'Party': party, 'Vote': vote}, ignore_index=True)
                cand = Candidate('District ' + dnumber, name, partyname, str(vote), winner)
                
                election.add_candidate(cand)
            election_list.append(election)
        # df = df.pivot_table(values='Vote', index='District', columns='Party', aggfunc='sum', fill_value=0)
        # df['2pvs'] = df['Democratic'] / (df['Democratic'] + df['Republican'])
        # chamber['df'] = df

    return election_list


def write_results(race_results, outfile):
    #write the results to a CSV file
    with open(outfile,'w') as csvout:
        csvwriter = csv.writer(csvout)
        for year, state, results in race_results:
            for election in results:
                for candidate in election.candidates:
                    csvwriter.writerow([year, state,candidate.district, candidate.party, candidate.name, candidate.votes, candidate.winner])

def scrape_results(url_file, outfile):
    #wrapper for fetching html/parsing it/writing results to file
    df = pd.read_csv(url_file)
    
    all_results = []
    for _, row in df.iterrows():
        race_results = extract_race_results(row['url'], row['state'])
        all_results.append((row['year'], row['state'], race_results))
                
    write_results(all_results, outfile)
    return all_results


if __name__ == '__main__':
    url_file = '2017_urls.csv'
    outfile = '2017_election_results.csv'
    scrape_results(url_file, outfile)
