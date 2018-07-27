import csv
import json

class Election:
    #election objects represent one row in the output file

    def __init__(self, year, state, district):
        #inputs are strings
        self.year = year
        self.state = state
        self.district = district

        #list of candidates who ran in race
        self.candidates = []

        #will be candidate who won
        self.winner = None


    def __repr__(self):
        return self.state + ', ' + self.year + ', ' + self.district

    
    def add_candidate(self, candidate):
        self.candidates.append(candidate)
        for candidate in self.candidates:
            candidate.calculate_vote_percent()

        if candidate.won:
            self.winner = candidate


class Candidate:
    #candidate objects represent one row in the input file

    def __init__(self, name, votes, party, won, election):
        #inputs are strings, except for won, which is a bool,
        #and election, which is an eleciton object

        #votes is absolute number of votes, not percentage
        self.name = name
        self.votes = votes
        self.party = self.clean_party_name(party)
        self.election = election

        #convert the votes string to an integer
        try:
            self.votes = float(votes)
        except: 
            self.votes = 0

        if won == 'true':
            self.won = True
        else:
            self.won = False
            
        #in cases where vote totals aren't reported (such as certain uncontested races)
        #set the winner's vote total to 1
        if self.won and self.votes == 0:
            self.votes = 1.0

        #calculate the percentage of the vote the candidate won
        self.calculate_vote_percent() 


    def calculate_vote_percent(self):
        #scale votes as a percentage of all votes cast in election
        #for Dems or Reps
        #totals will be incorrect until all major-party candidates
        #are added to the Election object
        total_votes = 0
        for candidate in self.election.candidates:
            if candidate.party == "D" or candidate.party == "R":
                total_votes += candidate.votes

        #if there aren't any reported votes and this candidate won, 
        #they get all the votes. otherwise, they get 0
        if total_votes == 0:
            if self.won:
                self.vote_percent = 1.0
            if not self.won:
                self.vote_percent = 0.0
        else:
            self.vote_percent = self.votes/total_votes


    def __repr__(self):
        info = self.name + ', ' + self.party + ', ' + str(self.votes) + ', ' + str(self.vote_percent) + '%'
        if self.won:
            return info + ', Won'
        else:
            return info + ', Lost'


    def clean_party_name(self, party):
        #party is a string
        #democrats are either 'Democratic' or 'Democratic Party'
        #republicans are either 'Republican' or 'Republican Party'
        #third party candidates are something else
        lowercase_party = party.lower()
        if lowercase_party.find("democratic") != -1:
            return "D"
        elif lowercase_party.find("republican") != -1:
            return "R"
        else:
            return "I"



def read_elections(election_file):
    #take a csv file with election results of the form
    #year, state, district, party, candidate name, votes, won (TRUE or FALSE)
    #return a list of election objects
    
    with open(election_file) as csvfile:
        csvreader = csv.reader(csvfile)
        candidate_details = [row for row in csvreader]
    
    #create a dictionary of elections; keys will be year|state|district
    elections_dict = {}
    
    for candidate_tuple in candidate_details:
        (year, state, district, party, candidate_name, votes, won) = candidate_tuple

        #for each candidate, check if the corresponding election is in the dictionary
        #if election exists, add the candidate, otherwise create a new election
        key = year + '|' + state + '|' + district

        #if the election has been encountered before, add the candidate to it;
        #otherwise, make a new election
        if key in elections_dict:
            election = elections_dict[key]
        else:
            election = Election(year, state, district)
            elections_dict[key] = election

        candidate = Candidate(candidate_name, votes, party, won.lower(), election)
        election.add_candidate(candidate)

    return elections_dict


def write_elections(elections_dict, outfile, name_to_abbr_dict):
    #take an election dictionary and write the results to a csv
    
    #rows to write to the csv file
    rows = []
    
    assembly_header = ["State", "District", "Year", "Party", "Incumbent", "Dem Votes", "GOP Votes", "Other Votes"]

    keys = elections_dict.keys()

    for election_key in keys:
        election = elections_dict[election_key]

        #incumbency wasn't recorded by scrapers, so we set it to -1
        incumbent = -1

        #change full state name to abbreviation to be consistent with 1971 - 2012 results
        state = name_to_abbr_dict[election.state]

        district = election.district
        year = election.year
        winning_party = election.winner.party
        
        #in contests with multiple candidates running under the same party, the party's total votes
        #is the sum of all votes those candidates recieved
        d_votes = sum([candidate.votes for candidate in election.candidates if candidate.party == 'D'])
        r_votes = sum([candidate.votes for candidate in election.candidates if candidate.party == 'R'])
        other_votes = sum([candidate.votes for candidate in election.candidates if candidate.party == 'I'])

        rows.append([state, district, year, winning_party, incumbent, d_votes, r_votes, other_votes])

    #sort by district, then by state, to make output file more readable
    rows.sort(key=lambda x: x[1])
    rows.sort(key=lambda x: x[0])
    
    
    
    with open(outfile, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows([assembly_header] + rows)

    return rows


def dict_merge(dict1, dict2):
    #merge two election dictionaries. There should
    #be no overlap in the keys
    dict1_keys = dict1.keys()
    for key in dict1:
        assert key not in dict2,'there should be no overlap in keys'
        dict2[key] = dict1[key]
    return dict2


def state_name_to_abbr(state_name, name_to_abbr_dict):
    return name_to_abbr_dict[state_name]
            

def combine_results(list_of_elections_files,dict_file,out_file):
    #given a list of files containing candidate information
    #and a state name -> abbreviation dictionary,
    #read each file, create a dictionary of election objects,
    #and write the results of each election to the out_file

    with open(dict_file) as openfile:
        name_to_abbr_dict = json.load(openfile)

    combined_elections_dict = {}

    for election_file in list_of_elections_files:
        election_dict = read_elections(election_file)

        #combine the election dictionary generated by each file into the 
        #election dictionary with results from all files
        combined_elections_dict = dict_merge(combined_elections_dict, election_dict)

    rows = write_elections(combined_elections_dict, out_file, name_to_abbr_dict)

    return combined_elections_dict
