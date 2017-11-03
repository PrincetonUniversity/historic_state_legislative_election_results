from bs4 import BeautifulSoup
import requests
import re
import csv
import time

class Candidate:
    #represents one row of the output file

    def __init__(self, district, name, party, votes, winner):
        #all arguments are strings, except winner, which is a Bool
        #strings get converted to utf8 to avoid unicode issues
        self.district = district.encode('utf8')
        self.name = name.encode('utf8')
        self.party = party.encode('utf8')
        self.votes = votes.encode('utf8')
        self.winner = winner

        #if the votes string has "No" in it, that means the 'candidate'
        #was actually "No Candidate" and the party didn't run anyone
        #in that election. They get 0 votes
        if self.votes.find('No') != -1:
            self.votes = '0' 

        #in unopoosed races, sometimes the candidate's name will 
        #end up duplicated as the "vote" string. 
        if self.name.find(self.votes) != -1:
            self.votes = '1'

        #otherwise, strip all non-numberic characters from
        #the votes string
        else:
            self.votes = re.sub("[^0-9]","",self.votes)


class Election:
    #holder object for Candidate objects

    def __init__(self):
        self.candidates = []

    def add_candidate(self,new_candidate):
        self.candidates.append(new_candidate)


def fetch_page(url):
    page = requests.get(url)
    return page.text


def pull_races(soup):
    #pulls the election results from the BeautifulSoup html tree and returns a list of Elections objects
    #the parsing tree is a disaster, but I'll try to explain
    
    #find the General election tag, then navigate away from that and get all the table entries
    general_election = soup.find_all(id='General_election')
    general_election_table = [x for x in general_election[0].parent.next_sibling.next_sibling.children if x != '\n']

    election_list = []

    #ignore the first and last entries, they're not election results
    for row in general_election_table[2:-1]:
        #ignore rows with certain formattings
        if row.text[3:] != u'\n\n\n\n' and row.text[2:6] != u'Note':
            children = [x for x in row.children if x != '\n']
            district = children[0].text
            general_election_candidates = children[1:]
            election = Election()

            for idx, candidate in enumerate(general_election_candidates):
                if candidate.text != u'\n':
                    #this chops the candidate info into the appropriate strings, then creates a Candidate object
                    candidate_text = candidate.text
                    candidate_name = candidate.text[:candidate_text.find(':')]
                    candidate_votes = candidate_text[candidate_text.find(':')+1:candidate_text.find(' ',candidate_text.find(":")+2)]
                    candidate_votes = candidate_votes.replace(',',"")

                    #because of the table structure, the first element contains Dems,
                    #the second contains Reps, and the third contains other/third-party
                    if idx == 0:
                        candidate_party = "Democratic"
                    elif idx == 1:
                        candidate_party = "Republican"
                    else:
                        candidate_party = "Other"

                    #candidates who win have a green check with title='Approved'
                    if candidate.find_all(title='Approved') != []:
                        candidate_won = True
                    else:
                        candidate_won = False

                    c = Candidate(district,candidate_name, candidate_party, candidate_votes, candidate_won)
                    election.add_candidate(c)
            election_list.append(election)

    return election_list


def extract_race_results(url):
    #fetch the html text, convert it into soup, and pull the race details
    page_text = fetch_page(url)
    print 'fetched text'
    soup = BeautifulSoup(page_text, 'lxml')
    print 'made soup'
    race_results = pull_races(soup)
    return race_results


def read_urls(url_file):
    #parse the URL file
    with open(url_file) as csvfile:
        reader = csv.reader(csvfile)
        urls = [(url[0],url[1],url[2]) for url in reader]
    return urls


def write_results(race_results, outfile):
    #given a list of tuples of the form (year, state, [list of election objects]),
    #write everything to file
    with open(outfile,'w') as csvout:
        csvwriter = csv.writer(csvout)
        for year, state, results in race_results:
            for election in results:
                for candidate in election.candidates:
                    #carve out for weird kansas formatting thing
                    if candidate.name == ' *Jim Gartner was appointed to replace retiring incumbent Annie Tietze. As a result, he appeared on the ballot as an incumbent, although he had not yet served a full term.':
                        pass
                    #carve out for Dem candidate in MN-32B, where a general election wasn't held in 2016
                    elif candidate.name == ' Laurie Warner' and candidate.party == 'Democratic':
                        pass
                    #carve out for Rep candidate inMN-32B, where a general election wasn't held in 2016
                    elif candidate.name == ' Bob Barrett (I)' and candidate.party == 'Republican':
                        pass

                    else:
                        csvwriter.writerow([year, state,candidate.district, candidate.party, candidate.name, candidate.votes, candidate.winner])
    return None

def scrape_results(url_file, outfile):
    #wrapper to run all of the fetching/parsing/writing results code
    urls = read_urls(url_file)
    all_results = []
    for year, state, url in urls:
        time.sleep(1)
        print year, state
        race_results = extract_race_results(url)
        all_results.append((year,state,race_results))
    write_results(all_results, outfile)
    return all_results

if __name__ == '__main__':
    url_file = '2016_urls.csv'
    outfile = '2016_election_results.csv'
    race_results = scrape_results(url_file, outfile)
