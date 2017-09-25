'''
Script to convert Carl Klarner's State Legislative Election Returns
candidate dataset into an elections dataset suitable for election-level
analysis.

This software is distributed under the GNU Public License,
Copyright Brian Remlinger and Sam Wang, 2017.

You are free to copy, distribute, and modify this code, so long as it
retains this header.
'''

import os
import os.path
import src.data_reducer as dr
import src.assembly_extractor as ae

if __name__ == '__main__':

    #check if the output folder exists and, if not, create it
    if not os.path.isdir('output_data'):
        os.mkdir('output_data')

    #SLER datafiles and file where we'll save the reduced dataset and new election dataset
    datafile_1972_2010 = "input_data/34297-0001-Data.csv"
    reduced_1972_2010 = "output_data/reduced_data_1972_to_2010.csv"
    savefile_1972_2010 = 'output_data/assembly_cleaned_data_1972_2010.csv'

    #note: 2011 to 2012 SLER extension was preprocessed to fill in column 15, 33, 34, 35, 36
    #using simple excel functions. See excel datafile included in github
    datafile_2011_2012 = "input_data/SLERs2011to2012.csv"
    reduced_2011_2012 = "output_data/reduced_data_2011_to_2012.csv"
    savefile_2011_2012 = 'output_data/assembly_cleaned_data_2011_2012.csv'


    ######
    #run the reducer script, wchich extracts the useful columns from the SLER dataset
    ######

    #columns to extract are: state, year, district id, candidate id, party code,
    #candidate incumbency, candidate won/lost, total votes cast in election,
    #total Democratic votes cast in election, total Republican votes cast,
    #total other votes cast, candidate name
    columns_to_extract = [2,5,15,22,25,26,27,28,33,34,35,36,23]
    reduced_header = ['state','year','district','candidate ID','party code','candidate incumbency','candidate votes won','won election?','total votes','dem votes','rep_votes','other_votes','candidate name']

    #extract data from the 1972 to 2010 dataset, then the 2011 to 2012 extension
    dr.reduce_dataset(datafile_1972_2010, columns_to_extract, reduced_1972_2010, reduced_header)
    dr.reduce_dataset(datafile_2011_2012, columns_to_extract, reduced_2011_2012, reduced_header)


    ######
    #run the candidate-to-assembly conversion script
    ######

    #has_header is True if the reduced dataset has a header, False otherwise
    has_header = True
    assembly_header = ["State", "District", "Year", "Party", "Incumbent", "Dem Votes", "GOP Votes", "Other Votes"]

    #smd_file is a csv specifying the first entirely single-member elections in each state
    smd_file = 'input_data/start_from_election_year.csv'
    #exclusion_file are races that are excluded from analysis for various unique reasons (a signgle
    #election conducted under a MMD plan, for example)
    exclusion_file = 'input_data/elections_to_exclude.csv'
    #corrections_file contains corrections to errors identified in the original dataset
    corrections_file_2011_2012 = 'input_data/SLERs2011_2012_corrections.csv'
    #All elections held before and during cutoff_year are excluded from analysis
    cutoff_year = 1970

    #convert candidate data to elections data
    elections_1972_2010 = ae.candidates_to_elections(reduced_1972_2010, savefile_1972_2010, assembly_header, smd_file=smd_file, exclusion_file=exclusion_file,has_header=has_header,cutoff_year=cutoff_year)
    elections_2011_2012 = ae.candidates_to_elections(reduced_2011_2012, savefile_2011_2012, assembly_header, smd_file=smd_file, exclusion_file=exclusion_file, corrections_file=corrections_file_2011_2012, has_header=has_header, cutoff_year=cutoff_year)
