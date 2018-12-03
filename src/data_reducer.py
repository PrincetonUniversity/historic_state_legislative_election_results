'''
Script to reduce Carl Klarner's State Legislative Election Returns dataset
to a file containing only a more manageable amount of information.

This software is distributed under the GNU Public License,
Copyright 2016 Brian Remlinger and Sam Wang, 2017.

You are free to copy, distribute, and modify this code, so long as it
retains this header.
'''

import csv

def SLER_extractor(f, columns_to_extract, header=False,filters=[]):
    '''
    Open the datafile, extract the relevant columns, and return the
    data as a list of lists.

    inputs: 
    "f" is the input filename as a string
    "columns_to_extract" is a list of column indices of interest
    "header" is a boolean, True if the input file has a header and False otherwise
    "filters" is a list of functions used to filter out rows that do not meet specific criteria

    output:
    "reduced_data" is a list of lists. Elements of each sub-list are strings.
    '''

    reduced_data = []

    #open and read the datafile
    with open(f, encoding='mac_roman') as csvfile:
        csvreader = csv.reader(csvfile)
        raw_data = [row for row in csvreader]

    #if header row exists, delete it
    if header:
        raw_data= raw_data[1:]

    #for each row, apply filters. If the row fails any of the filters,
    #discard it. Otherwise, reduce the row to the columns of interest
    #and append it to the list of results
    for line in raw_data:
        passed_filters = True
        for f in filters:
            if not f(line):
                passed_filters = False
        if passed_filters:
            reduced_data.append([line[idx] for idx in columns_to_extract])

    return reduced_data


def general_election(line):
    #takes as input a raw (un-reduced) line from the SLER dataset
    #returns True if line represents a datapoint from a general election
    #returns False otherwise
    return line[20] == 'G'


def assembly_election(line):
    #takes as input a raw (un-reduced) line from the SLER dataset
    #returns True if the line represents a datapoint from a lower-house election
    #returns False otherwise
    return line[7] == '9'


def reduce_dataset(datafile, columns_to_extract, outfile, header_text, header=True, filters = [general_election, assembly_election]):
    '''
    Reads in a datafile from the State Legislative Election Returns dataset, strips it down
    to rows and columns of interest, and writes the output to a csv.

    Inputs:
    "datafile" is the input filename as a string
    "columns_to_extract" is a list of column indices of interest
    "header_text" is a list of strings, each string corresponding to a column header in the output file
    "outfile" is the output filename as a string
    "header" is a boolean, True if the input file has a header and False otherwise
    "filters" is a list of functions used to filter out rows that do not meet specific criteria

    '''

    #open datafile, extract relevant columns, filter out datapoints that do not match filter criteria
    reduced_data = SLER_extractor(datafile, columns_to_extract, header, filters)

    #create a list of unique state names, then sort alphabetically
    states = list(set([election[0] for election in reduced_data if election[0] != ""]))
    states.sort()

    #reorder election results by state
    all_elections = []
    for state in states:
        elections = [e for e in reduced_data if e[0] == state]
        all_elections.extend(elections)
    
    #write sorted election results to outfile
    with open(outfile,'w') as csvfile:
        w = csv.writer(csvfile)
        w.writerow(header_text)
        w.writerows(all_elections)

    return None



if __name__ == "__main__":

    #check if the output folder exists and, if not, create it
    import os
    import os.path
    if not os.path.isdir('output_data'):
        os.mkdir('output_data')

    datafile_1972_2010 = "input_data/34297-0001-Data.csv"
    outfile_1972_2010 = "output_data/reduced_data_1972_to_2010.csv"

    #note: 2011 to 2012 SLER extension was preprocessed to fill in column 15, 33, 34, 35, 36
    #using simple excel functions. See excel datafile included in github
    datafile_2011_2012 = "input_data/SLERs2011to2012.csv"
    outfile_2011_2012 = "output_data/reduced_data_2011_to_2012.csv"

    #columns to extract are: state, year, district id, candidate id, party code, 
    #candidate incumbency, candidate won/lost, total votes cast in election,
    #total Democratic votes cast in election, total Republican votes cast,
    #total other votes cast, candidate name
    columns_to_extract = [2,5,15,22,25,26,27,28,33,34,35,36,23]
    header_text = ['state','year','district','candidate ID','party code','candidate incumbency','candidate votes won','won election?','total votes','dem votes','rep_votes','other_votes','candidate name']

    #extract data from the 1972 to 2010 dataset, then the 2011 to 2012 extension
    reduce_dataset(datafile_1972_2010, columns_to_extract, outfile_1972_2010, header_text)
    reduce_dataset(datafile_2011_2012, columns_to_extract, outfile_2011_2012, header_text)
