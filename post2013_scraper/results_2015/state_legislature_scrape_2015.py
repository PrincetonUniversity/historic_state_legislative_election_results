import pandas as pd
import requests
import re
import csv
from bs4 import BeautifulSoup as bs

class Candidate:

    def __init__(self, district, name, party, votes, winner):
        #takes strings, except for winner, which is a Boolean
        #converts the strings to UTF-8 to avoid unicode issues
        self.district = district.encode('utf8')
        self.name = name.encode('utf8')
        self.party = party.encode('utf8')
        self.votes = votes.encode('utf8')
        self.winner = winner


class Election:
    #holder for Candidate objects

    def __init__(self):
        self.candidates = []

    def add_candidate(self,new_candidate):
        self.candidates.append(new_candidate)


def fetch_page(url):
    page = requests.get(url)
    return page.text


def pull_races(soup):
    #parses a BeautifulSoup object and returns a list of results;
    #the HTML tree is kind of a disaster but I'll try to explain
    
    #find_all_districts
    all_race_divs = soup.find_all(id=re.compile('District_*'))

    election_list = []

    for idx,race in enumerate(all_race_divs):

        election = Election()
        
        #the first district is weird because of formatting, so it gets treated differently
        if idx == 0:
            district = 'District 1'
            results_tag = all_race_divs[1].parent.previous_sibling.previous_sibling

        else:
            district = race.parent.text
            tag = race.parent

            general_race_element_found = False
            
            #there's an unknown number of tags between the "District" tag and the "general election" tag,
            #so iterate until you find the general election
            while general_race_element_found == False:
                #some tags don't have text, and will throw an exception. Iterate past them.
                try:
                    #there's some page-specific logic in here that's not worth explaining
                    if tag.text.find("General") != -1 or tag.text.find('general') != -1:
                        general_race_element_found = True
                        if tag.text.find('\n') != -1 and tag.text.find('\n') != len(tag.text)-1:
                            results_tag = tag
                        else:
                            results_tag = tag.next_sibling
                            try:
                                if results_tag.text[:5] == u'Note:':
                                    results_tag = results_tag.next_sibling.next_sibling
                                else:
                                    results_tag = results_tag.next_sibling
                            except:
                                results_tag = results_tag.next_sibling
                                try:
                                    children = [x for x in results_tag.children if x != '\n']
                                    if results_tag.text[:5] == u'Note:' and len(children) == 1:
                                        results_tag = results_tag.next_sibling.next_sibling
                                except:
                                    pass
                    else:
                        tag = tag.next_sibling
                except:
                    tag = tag.next_sibling
       
        #all candidates are children of the general election tag, but not all children are candidates
        general_election_candidates = [candidate_tag for candidate_tag in results_tag.children if candidate_tag != u'\n']

        for candidate in general_election_candidates:
            #if you find a candidate, chop the text into different bits and create a Candidate object
            if candidate.text.find('General election') == -1 and candidate.text.find('Note:') == -1:
                candidate_text = candidate.text
                candidate_name = candidate.text[1:candidate_text.find(':')].strip()
                candidate_votes = candidate.text[candidate_text.find(':')+2:]
                candidate_votes = candidate_votes.replace(',',"")

                #candidates who belong to a party have 'title' text which is that party;
                #if they don't have title text, they're unaffiliated
                try:
                    candidate_party = candidate.a['title']
                except:
                    candidate_party = 'unaffiliated'

                #candidates who win get a green checkmark; find that if it's there
                if candidate.span['style'].find('color:green') != -1:
                    candidate_won = True
                else:
                    candidate_won = False

                c = Candidate(district,candidate_name, candidate_party, candidate_votes, candidate_won)
                election.add_candidate(c)
        election_list.append(election)

    return election_list


def read_urls(url_file):
    #parse the URL file
    with open(url_file) as csvfile:
        reader = csv.reader(csvfile)
        urls = [(url[0],url[1],url[2]) for url in reader]
    return urls

def write_results(race_results, outfile):
    #write the results to a CSV file
    with open(outfile,'w') as csvout:
        csvwriter = csv.writer(csvout)
        for year, state, results in race_results:
            for election in results:
                for candidate in election.candidates:
                    csvwriter.writerow([year, state,candidate.district, candidate.party, candidate.name, candidate.votes, candidate.winner])
    return None

def pull_incumbency(soup):
    # find all instances of the word incumbent, and cycle back to find the name that it refers to, making a list of incumbent names.
    matches = soup(text=re.compile('Incumbent '))
    
    incumbents = []
    
    def get_name(tag):
        text = ''
        while len(text) < 2:
            if hasattr(tag, 'previous_sibling'):
                tag = tag.previous_sibling
            else:
                return None
            if hasattr(tag, 'text'):
                text = tag.text
                
        return text

    matches[:5]
    get_name(matches[2])
    
    for match in matches:
        name = get_name(match)

        if (name is not None) and (name != 'Note:'):
            incumbents.append(name)                
            
    return incumbents


def scrape_results(url_file, outfile):
    #wrapper for fetching html/parsing it/writing results to file
    urls = read_urls(url_file)
    all_results = []
    incumbency = pd.DataFrame()
    
    for year, state, url in urls:
        print(state)
        
        page_text = fetch_page(url)
        soup = bs(page_text, 'lxml')
        race_results = pull_races(soup)
        
        all_results.append((year, state, race_results))
        
        incumbents = pull_incumbency(soup)
        
        for incumbent in incumbents:
            incumbency = incumbency.append({'Year': year,
                                            'State': state,
                                            'Name': incumbent,
                                            'Incumbent': True},
                                           ignore_index=True)

    write_results(all_results, outfile)
    
    df = pd.read_csv(outfile, header=None, names=['Year', 'State', 'District', 'Party', 'Name', 'Votes', 'Winner'], dtype=str)
    merged = df.merge(incumbency, on=['Year', 'State', 'Name'], how='left')
    merged['Incumbent'] = merged['Incumbent'].fillna(0)

    merged.to_csv(outfile, index=False)
    
    return all_results

if __name__ == '__main__':
    url_file = '/Users/wtadler/Repos/historic_state_legislative_election_results/post2013_scraper/results_2015/2015_urls.csv'
    outfile = '2015_election_results.csv'
    scrape_results(url_file, outfile)
