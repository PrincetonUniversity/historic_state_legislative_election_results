from bs4 import BeautifulSoup
import requests
import re
import csv
import time

class Candidate:

    def __init__(self, district, name, party, votes, winner):
        #all inputs are strings, except winner, which is a Boolean
        #strings are converted to utf8 to avoid Unicode issues
        self.district = district.encode('utf8')
        self.name = name.encode('utf8')
        self.party = party.encode('utf8')
        self.votes = votes.encode('utf8')
        self.winner = winner

        #in uncontested races, the candidate's name
        #sometimes ends up in the vote column
        #in those cases, the candidate is given a single vote
        if self.name.find(self.votes) != -1:
            self.votes = 1
        #in other cases, a party runs no candidate and
        #"No candidate" ends up in the vote column.
        #these "candidates" get 0 votes
        elif self.votes.find('No candidate') != -1:
            self.votes = 0
        #otherwise, you just have a string of numbers
        #and stuff. Strip all non-numeric characters
        else:
            self.votes = re.sub("[^0-9]","",self.votes)


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
    #parse the BeautifulSoup input for races, return a list of races
    #the parsing is a mess, but I'll try to explain
    
    #find all districts
    all_race_divs = soup.find_all(id=re.compile('District_*'))

    election_list = []

    for idx,race in enumerate(all_race_divs):

        election = Election()
        #the first race has weird formatting things and needs to be treated differently
        if idx == 0:
            district = 'District 1'
            results_tag = all_race_divs[1].parent.previous_sibling.previous_sibling

        else:
            district = race.parent.text
            tag = race.parent
            
            general_race_element_found = False
            
            #there's an unknown number of tags betwen the "District" tag and the general election
            #tag. Itterate through them until you find the General tag. There are some weird
            #edge cases in the logic, but don't worry about them too much
            while general_race_element_found == False:
                try:
                    if tag.text.find("General") != -1:
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
                            if results_tag.text[:5] == u'Note:':
                                results_tag = results_tag.next_sibling.next_sibling
                    else:
                        tag = tag.next_sibling
                except:
                    tag = tag.next_sibling
       
        #all the candidates are leaves of the general election tag, but not all leaves are candidates
        general_election_candidates = [candidate_tag for candidate_tag in results_tag.children if candidate_tag != u'\n']

        for candidate in general_election_candidates:
            if candidate.text.find('General election') == -1:
                #if we think the leaf is a candidate, parse the text and then create a Candidate object
                candidate_text = candidate.text
                candidate_name = candidate.text[:candidate_text.find(':')]
                candidate_votes = candidate.text[candidate_text.find(':')+2:]
                candidate_votes = candidate_votes.replace(',',"")

                #the candidate's title tag is their party; if they don't have
                #a title tag, they're a third party candidate
                try:
                    candidate_party = candidate.a['title']
                except:
                    candidate_party = 'unaffiliated'

                #if the candidate won, they get a little green check and the
                #title text 'Approved'
                if candidate.find_all(title='Approved') != []:
                    candidate_won = True
                else:
                    candidate_won = False

                c = Candidate(district,candidate_name, candidate_party, candidate_votes, candidate_won)
                election.add_candidate(c)
        election_list.append(election)

    return election_list


def extract_race_results(url):
    #fetch the html and parse it
    page_text = fetch_page(url)
    soup = BeautifulSoup(page_text, 'lxml')
    race_results = pull_races(soup)
    return race_results

def read_urls(url_file):
    #parse the url file
    with open(url_file) as csvfile:
        reader = csv.reader(csvfile)
        urls = [(url[0],url[1],url[2]) for url in reader]
    return urls

def write_results(race_results, outfile):
    #write the parser results to the output file
    with open(outfile,'w') as csvout:
        csvwriter = csv.writer(csvout)
        for year, state, results in race_results:
            for election in results:
                for candidate in election.candidates:
                    #carveout for weird formatting issue where noncandidates were being listed as candidates
                    if candidate.name == '  Republican primary candidates' or candidate.name == '  Democratic primary candidates' or candidate.name == '  Conservative primary candidates' or candidate.name == '  Green primary candidate':
                        pass
                    else:
                        csvwriter.writerow([year, state,candidate.district, candidate.party, candidate.name, candidate.votes, candidate.winner])
    return None


def scrape_results(url_file, out_file):
    #wrapper for running all the scraping/parsing/writing to file
    urls = read_urls(url_file)
    all_results = []
    for year, state, url in urls:
        time.sleep(1)
        print(state)
        race_results = extract_race_results(url)
        all_results.append((year, state,race_results))
    write_results(all_results, out_file)


if __name__ == '__main__':
    url_file = '2016_NY_url.csv'
    out_file = 'state_legislature_scrape_2016_ny.csv'
