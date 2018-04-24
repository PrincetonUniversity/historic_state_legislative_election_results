'''
Script to convert Carl Klarner's State Legislative Election Returns
candidate dataset into an elections dataset suitable for election-level
analysis.

This software is distributed under the GNU Public License,
Copyright Brian Remlinger and Sam Wang, 2017.

You are free to copy, distribute, and modify this code, so long as it
retains this header.
'''


import csv

class Election:
    '''
    Class used to contain data for a specific election; identifying info for an election is
    state, year, and district
    '''
    def __init__(self, state, year, district, total_votes, dem_votes, rep_votes, other_votes):
        '''
        all inputs are strings
        '''
        self.state = state
        self.year = year
        self.district = district
        self.total_votes = total_votes
        self.dem_votes = dem_votes
        self.rep_votes = rep_votes
        self.other_votes = other_votes

        self.candidates = []
        self.winner = None

        self.id_string = self.state + "|" + self.year + "|" + self.district 

    def __repr__(self):
        return self.id_string

    def add_candidate(self, candidate):
        self.candidates.append(candidate)

    def determine_winner(self):
        '''
        Determines with candidate in self.candidates won the election. 
        In some cases, the same candidate
        will appear multiple times because they ran under multiple party
        platforms. In those cases, the winner should reflect the major
        party affiliation of the candidate (if it exists).

        Also, in some cases states don't provide the number of votes
        for uncontested races, so the vote totals will be blank. In
        those situations, replace total votes with 100, votes for the
        winning party with 100, and votes for the other parties with 0
        '''
        
        #make sure that the winner has not already been set; if it has,
        #that may make function results inaccurate
        self.winner = None
        for candidate in self.candidates:
            if int(candidate.won) == 1:

                #if there's no winner, assign this candidate as the winner
                if self.winner == None:
                    self.winner = candidate

                #if there is a winner, check that the winning candidate is not
                #the same as this candidate
                else:
                    if self.winner.unique_id == candidate.unique_id:
                        #if the candidate is the same, but this version is an independent,
                        #we don't care (either the other version is also an I or it's a 
                        #major party
                        if candidate.party == "I" or candidate.party == "Other":
                            pass

                        #if this version of the candidate is from a major party,
                        #the other version is either from the other major party
                        #or and independent party
                        elif candidate.party == "R" or candidate.party == "D":
                            #if the current winner is an minor party, replace it with this candidate
                            if self.winner.party == "I" or self.winner.party == "Other":
                                self.winner = candidate

                            #if the candidate ran on both major party platforms, change the 
                            #party of the candidate to "Both"
                            elif self.winner.party == "R" and candidate.party == "D":
                                self.winner.party = "Both"
                            elif self.winner.party == "D" and candidate.party == "R":
                                self.winner.party = "Both"
                            
        #if the election does not have vote totals included (due to missing records
        #in the original dataset, almost entirely because certain states do not record 
        #vote totals for candidates in uncontested elections), add artifical vote counts
        if self.total_votes == '':
            self.total_votes = '100'
            if self.winner.party == "D":
                self.dem_votes = '100'
                self.rep_votes = '0'
                self.other_votes = '0'
            elif self.winner.party == "R":
                self.dem_votes = '0'
                self.rep_votes = '100'
                self.other_votes = '0'
            else:
                self.dem_votes = '0'
                self.rep_votes = '0'
                self.other_votes = '100'
        return None


class Candidate:
    '''
    Class representing candidates. The candidate is uniquely identified by
    the election they're associated with, their name, and their party
    '''
    def __init__(self, election, name, party, incumbency, votes, won, unique_id):
        '''
        all inputs are strings except for the election object.
        'name' is the candidate name; 'party' is the candidate's party,
        'incumbency' is 1 if candidate is incumbent, 0 otherwise,
        'votes' is the number of votes the candidate receives,
        'won' is 1 if the candidate won the election, 0 otherwise,
        'unique_id' is a string identifying the candidate in the SLER dataset
        '''
        self.election = election
        self.name = name
        self.party = party_cleaner(party)
        self.incumbency = incumbency
        self.votes = votes
        self.won = won
        self.unique_id = unique_id

        self.id_string = election.id_string + "|" + name + "|" + party_cleaner(party)

    def __repr__(self):
        return self.id_string


def create_elections_dict(candidate_data):
    #################################################################
    #################################################################
    ###IMPORTANT: this function assumes candidate_data is of the form 
    ###[state,year,district,candidate_id, party, incumbency, candidate votes, won binary,
    ###democratic votes cast in election, republican votes cast in election, other votes
    ###cast in election, candidate name]. If the form of the candidate_data rows
    ###change, the indices below used to assign data to the Candidate and Election
    ###constructors must be modified
    #################################################################
    #################################################################
    #takes a list of lists of candidate information and creates associated Candidate
    #and Election objects. Returns a dictionary of election identifiers which maps
    #to Election objects

    elections = {}

    #each row of the input represents information for a candidate. Check if the corresponding
    #Election object has been created. If not, create it. Then create the Candidate object
    #and attach the Candidate to the corresponding Election
    for line in candidate_data:
        #create an election id of the form state|year|district
        election_id = election_id_generator(line, [0,1,2])

        #if the election already exists; if it doesn't, make it and add it to the dict
        if election_id in elections:
            election = elections[election_id]
        else:
            election = Election(line[0], line[1], line[2], line[8], line[9], line[10], line[11])
            elections[election_id] = election

        #generate the Candidate object and add it to the Election object
        candidate = Candidate(election, line[12], line[4], line[5], line[6], line[7],line[3])
        election.add_candidate(candidate)

    #determine the winner of each election
    for election in elections:
        elections[election].determine_winner()

    return elections


def election_id_generator(candidate_data_line, election_id_indexes):
    #given a row of candidate information and a the indices of identifying information, 
    #use specified entries to ID election
    election_id = ''
    for idx in election_id_indexes:
        election_id = election_id + candidate_data_line[idx] + "|"

    #drop the extra '|' at the end of the election ID
    return election_id[:-1]


def single_district_election(election,years_dict):
    #many states had multi-member districts well into the 80s 
    #or 90s. The impact of MMDs on statistical tests is unclear,
    #but for now we remove those elections from the data.

    #This function takes an election object and a dictionary of the form
    #{state: first year using single member districts}
    #if year is 0, state still uses single member districts
    #returns True if state is NOT using multimember districts in election year
    #returns False if state IS using multimembmer districts in eleciton year
    election_year = int(election.year)
    first_SMD_year = int(years_dict[election.state])

    #states that are still using multimember districts have years set to 0
    if first_SMD_year == 0:
        return False
    return election_year >= first_SMD_year


def election_writer(elections, outfile, header = None):
    '''
    writes a csv file, one election per line, in the following format:
    State, District, Year, Month, Winner (name), Winner (Party), Incumbency, 
    Dem Votes, GOP Votes, Other Votes
    '''

    csv_out = []

    for e_key in elections:
        e = elections[e_key]
        if e.district == '':
            e.district = -1
        line = [e.state, e.district, e.year,e.winner.party,
                e.winner.incumbency, e.dem_votes, e.rep_votes, e.other_votes]
        csv_out.append(line)

    csv_out.sort(key=lambda x: (x[0],x[2]))

    with open(outfile, "w") as csvfile:
        w = csv.writer(csvfile, delimiter = ",")
        if header != None:
            w.writerow(header)
        for row in csv_out:
            w.writerow(row)

    return csv_out


def correct_data(elections, corrections_file):
    #several candidates in the 2011 - 2012 data extension have incorrect
    #party codes. This function corrects that.
    #REWRITE DESCRIPTION BELOW
    #takes a dict of elections objects and a csv file of corrections.
    #the csv file is of the form year, name, party
    #for each election, checks if the winner is in the corrections file
    #if the winner is in the file, corrects the party of the winner

    with open(corrections_file) as csvfile:
        r = csv.reader(csvfile)
        lines = [line for line in r]

    #create a dictionary of corrections that uses the same
    #keys as the input elections dictionary
    corrections_dict = {}
    for year,state,name,party in lines:
        corrections_dict[year+"|"+state+"|"+name] = party

    keys = corrections_dict.keys()

    #for each election, check if the election is in the corrections dictionary
    #if it is, change the party of the winning candidate to the corrected party
    for election_label in elections:
        election = elections[election_label]
        assert election.winner != None, "Election.determine_winner() has not been run on this data"
        name_of_winner = election.winner.name
        year = election.year
        state = election.state
        dict_key = year + "|" + state + "|" + name_of_winner
        if dict_key in keys:
            election.winner.party = corrections_dict[dict_key]
            if election.winner.party == "R":
                election.rep_votes = election.winner.votes
            elif election.winner.party == "D":
                election.dem_votes = election.winner.votes
            election.other_votes = 0

    return elections


def party_cleaner(party):
    #takes a string representing the simplified party code
    #of a candidate from the SLER. Returns a more recognizable
    #party identifier
    #"Other" candidates are identified as write-in, fusion, or other in SLER
    if int(party) == 100:
        return 'D'
    if int(party) == 200:
        return 'R'
    if int(party) == 400:
        return 'I'
    else:
        return 'Other'


def candidates_to_elections(datafile, savefile, header, smd_file=None, exclusion_file=None,has_header=True, corrections_file=None, cutoff_year=None):
    '''
    Takes a file of candidate data, converts the data to elections, and then writes those
    elections that meet certain criteria to a csv file

    Inputs
    datafile: the filename, as a string, of the file the candidate data is saved in
    savefile: the filename, as a string, of the file to save the election data
    header: a list of strings, each one to be used as a header in the output file
    smd_file: the name of the file listing the first year each state used single member districts
    as a string
    exclusion_file: a string naming a file of elections to exclude, generally because of a weird
    number of districts of, in the case of Georgia in 2002, because a state temporarily switched
    back to multi-member districts
    has_header: a boolean, true if the input file has a header to be discarded, otherwise False
    corrections: the name of the csv file containing the corrected party info as a string
    cutoff_year: an int representing the first year to record elections. Elections before that
    year are dropped
    '''

    with open(datafile) as csvfile:
        csv_reader = csv.reader(csvfile)
        assembly_data = [line for line in csv_reader]

    #drop the header row
    if has_header:
        assembly_data =  assembly_data[1:]

    #generate dictionary with first election using single member districts
    if smd_file != None:
        smd_dict = {}
        with open(smd_file) as csvfile:
            csvreader = csv.reader(csvfile)
            lines = [line for line in csvreader]
        for state, year in lines:
            smd_dict[state] = year

    #generate dict with years to exclude (for reasons other than MMD)
    if exclusion_file != None:
        years_to_exclude = {}
        with open(exclusion_file) as csvfile:
            csvreader = csv.reader(csvfile)
            lines = [line for line in csvreader]
        for state, year in lines:
            if state in years_to_exclude:
                years_to_exclude[state].append(year)
            else:
                years_to_exclude[state] = [year]

    #create the elections dictionary
    elections = create_elections_dict(assembly_data)

    #make corrections to elections if corrections are needed
    if corrections_file != None:
        elections = correct_data(elections, corrections_file)

    #if only extracting single member elections, create new dictionary
    #containing only those elections
    if smd_file != None:
        single_member_elections = {}
        for election in elections:
            if single_district_election(elections[election], smd_dict):
                single_member_elections[election] = elections[election]
        elections = single_member_elections

    #if there are years to exclude, exclude them
    if exclusion_file != None:
        cleaned_elections = {}
        for election in elections:
            if elections[election].state not in years_to_exclude:
                cleaned_elections[election] = elections[election]
            elif elections[election].year not in years_to_exclude[elections[election].state]:
                cleaned_elections[election] = elections[election]
        elections = cleaned_elections

    #if a cutoff year is specified, drop elections preceding that year
    if cutoff_year != None:
        year_cutoff_elections ={}
        for election in elections:
            if int(elections[election].year) > cutoff_year:
                year_cutoff_elections[election] = elections[election]
        elections = year_cutoff_elections

    election_writer(elections, savefile, header=header)

    return elections
    


if __name__ == "__main__":
    datafile_1972_2010 = "output_data/reduced_data_1972_to_2010.csv"
    savefile_1972_2010 = 'output_data/assembly_cleaned_data_1972_2010.csv'
    datafile_2011_2012 = "output_data/reduced_data_2011_to_2012.csv"
    savefile_2011_2012 = 'output_data/assembly_cleaned_data_2011_2012.csv'
    has_header = True
    header = ["State", "District", "Year", "Party", "Incumbent", "Dem Votes", "GOP Votes", "Other Votes"]
    smd_file = 'input_data/start_from_election_year.csv'
    exclusion_file = 'input_data/elections_to_exclude.csv'
    corrections_file_2011_2012 = 'input_data/SLERs2011_2012_recoding.csv'
    cutoff_year = 1970

    elections_1972_2010 = candidates_to_elections(datafile_1972_2010, savefile_1972_2010, header, smd_file=smd_file, exclusion_file=exclusion_file,has_header=has_header,cutoff_year=cutoff_year)

    elections_2011_2012 = candidates_to_elections(datafile_2011_2012, savefile_2011_2012, header, smd_file=smd_file, exclusion_file=exclusion_file, corrections_file=corrections_file_2011_2012, has_header=has_header, cutoff_year=cutoff_year)

    

#    f = "reduced_data_2012_to_2013.csv"
#    correct_data_trigger = True
#    savefile = 'assembly_cleaned_data_2012_2013.csv'

    #read in the data
#    with open(f) as csvfile:
#        csv_reader = csv.reader(csvfile)
#        data = [line for line in csv_reader]
#
#    #remove header
#    assembly_data =  data[1:]
#
#    #get dictionary with first election using single member districts
#    years_dict = {}
#    with open('input_data/start_from_election_year.csv') as csvfile:
#        csvreader = csv.reader(csvfile)
#        lines = [line for line in csvreader]
#    for state, year in lines:
#        years_dict[state] = year
#
#    #get dict with years to exclude (for reasons other than MMD)
#    years_to_exclude = {}
#    with open('input_data/elections_to_exclude.csv') as csvfile:
#        csvreader = csv.reader(csvfile)
#        lines = [line for line in csvreader]
#    for state, year in lines:
#        if state in years_to_exclude:
#            years_to_exclude[state].append(year)
#        else:
#            years_to_exclude[state] = [year]
#        
#
#############################################
## candidates_to_elections MUST BE UPDATED if input rows are not exactly:
##['state','year','district','candidate ID','party code','candidate incumbency','candidate votes won',
##'won election?','total votes','dem votes','rep_votes','other_votes','candidate name']
############################################
#
#    elections = create_elections_dict(assembly_data)
#    if correct_data_trigger:
#        elections = correct_data(elections, 'SLERs2011_2012_recoding.csv')
#
#    #filter out elections pre-1971 and elections conducted under MMD
#    single_member_elections = {}
#    for election in elections:
#        if single_district_election(elections[election], years_dict):
#            if int(elections[election].year) > 1970:
#                if elections[election].state not in years_to_exclude:
#                    single_member_elections[election] = elections[election]
#                elif elections[election].year not in years_to_exclude[elections[election].state]:
#                    single_member_elections[election] = elections[election]
#    election_writer(single_member_elections, savefile, header=header)
##    election_writer(elections, savefile, header=header)
