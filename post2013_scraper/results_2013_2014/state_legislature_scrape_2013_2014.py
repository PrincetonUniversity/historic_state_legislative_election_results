import pandas as pd
import requests
import re
import csv
from bs4 import BeautifulSoup as bs


class Candidate:
    #represents one row in the output file

    def __init__(self, district, name, party, votes, winner):
        #all inputs are strings, except for winner, which is a Boolean
        #encode all strings in utf8 to avoid unicode issues
        self.district = district.encode('utf8')
        self.name = name.encode('utf8')
        self.party = party.encode('utf8')
        self.votes = votes.encode('utf8')
        self.winner = winner




class Election:
    #holder for election objects

    def __init__(self):
        self.candidates = []

    def add_candidate(self,new_candidate):
        self.candidates.append(new_candidate)



def fetch_page(url):
    page = requests.get(url)
    return page.text


def pull_races(soup):
    all_race_divs = soup.find_all(id=re.compile('District_*'))

    election_list = []
    
    for idx,race in enumerate(all_race_divs):
        election = Election()
        #the first district on each page is different than all the others for formatting reasons
        if idx == 0:
            district = 'District 1'
            results_tag = all_race_divs[1].parent.previous_sibling.previous_sibling
        else:
        #the html tree parsing is messy. I'll try to explain as much as possible
            #one level up the tree is the district name
            district = race.parent.text
            tag = race.parent
            
            general_race_element_found = False
            
            #there's an unknown number of tags between the "District" header
            #and the general election results (for example, because there are 
            #an unknown number of candidates in each primary)
            #iterate through the tags until you find the General Election one
            while general_race_element_found == False:
                #some tags don't have text and will throw an error; we don't want those
                try:
                    if tag.text.find("General") != -1:
                        general_race_element_found = True
                        
                        #this is a bunch of logic to deal with edge formatting cases and issues
                        if tag.text.find('\n') != -1 and tag.text.rfind('\n') != len(tag.text)-1:
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
       
        #the candidate info are all the leaves of the tag, but not all the leaves are candidates
        general_election_candidates = [candidate_tag for candidate_tag in results_tag.children if candidate_tag != u'\n']
        for candidate in general_election_candidates:
            #don't mistake that General Election leaf for a candidate
            if candidate.text.find('General election') == -1:
                if ':' in candidate.text: # if there is a colon
                    candidate_name, candidate_votes = candidate.text.split(':')
                elif re.search('\d', candidate.text): # if there's no colon but there's a vote count
                    split_pt = re.search('\d', candidate.text).start()
                    candidate_name = candidate.text[:split_pt]
                    candidate_votes = candidate.text[split_pt:]
                else: # if there's no vote count
                    candidate_name = candidate.text
                    candidate_votes = '1'
                    
                candidate_name = candidate_name.strip()
                if candidate_name == 'No candidate':
                    candidate_votes = '0'
                candidate_votes = ''.join(i for i in candidate_votes if i.isdigit())

                try:
                    candidate_party = candidate.a['title']
                except:
                    candidate_party = 'unaffiliated'
                
                #winning candidates are flagged with a checkmark and a special title element
                if candidate.find_all(title='Won') != [] or candidate.find_all(title='Approved')!=[]:
                    candidate_won = True
                else:
                    candidate_won = False

                #create a candidate using all that info you found, then add it to the election object
                c = Candidate(district,candidate_name, candidate_party, candidate_votes, candidate_won)
                election.add_candidate(c)

        election_list.append(election)

    return election_list


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

    for match in matches:
        name = get_name(match)

        if (name is not None) and (name != 'Note:'):
            incumbents.append(name)                
            
    return incumbents


def read_urls(url_file):
    #parse the url file
    with open(url_file) as csvfile:
        reader = csv.reader(csvfile)
        urls = [(url[0],url[1],url[2]) for url in reader]
    return urls


def write_results(race_results, outfile):
    #takes a list of tuples of the form (year, state, [list of election objects])
    #and a string as an output file. Writes the election results to the output file
    with open(outfile,'w') as csvout:
        csvwriter = csv.writer(csvout)
        for year, state, results in race_results:
            for election in results:
                for candidate in election.candidates:
                    if state == "Florida" and candidate.district == 'District 13':
                    #carve out for District 13 in Florida, where there was no general election in 2014
                        pass
                    elif state == "New York" and candidate.name == '  September 9 Republican primary candidates':
                    #carve out for District 147 in NY, which has some funky formating thing
                        pass
                    else:
                        csvwriter.writerow([year, state,candidate.district, candidate.party, candidate.name, candidate.votes, candidate.winner])
    return None

def scrape_results(url_file, outfile):
    #wrapper to run the whole fetching/scraping/results writing pipeline
    urls = read_urls(url_file)
    all_results = []
    incumbency = pd.DataFrame()
    
    for year, state, url in urls:
        print(year, state)
        
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
    url_file = '2013_2014_urls.csv'
    outfile = 'election_results_2013_2014.csv'
    all_results = scrape_results(url_file, outfile)
