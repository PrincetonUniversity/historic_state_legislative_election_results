import re
import pandas as pd
import numpy as np
import time

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


def extract_race_results(url):
    election_list = []

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
            election.add_candidate(cand)

        election_list.append(election)

    return election_list

def write_results(race_results, outfile):
    #write the results to a CSV file
    with open(outfile,'w') as csvout:
        csvwriter = csv.writer(csvout)
        for year, state, results in race_results:
            for election in results:
                for candidate in election.candidates:
                    csvwriter.writerow([year, state,candidate.district, candidate.party, candidate.name, candidate.votes, candidate.winner])
    return None

def scrape_results(url_file, outfile):
    #wrapper for fetching html/parsing it/writing results to file
    urls = read_urls(url_file)
    all_results = []
    for year, state, url in urls:
        print(state)
        time.sleep(1)
        race_results = extract_race_results(url)
        all_results.append((year, state, race_results))
    write_results(all_results, outfile)
    return all_results


def read_urls(url_file):
    #parse the URL file
    with open(url_file) as csvfile:
        reader = csv.reader(csvfile)
        urls = [(url[0],url[1],url[2]) for url in reader]
    return urls


if __name__ == '__main__':
    url_file = '2017_urls_va.csv'
    outfile = '2017_election_results.csv'
    scrape_results(url_file, outfile)
