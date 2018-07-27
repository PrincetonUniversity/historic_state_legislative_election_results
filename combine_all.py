import pandas as pd
import re
import natsort as ns

files = ['output_data/assembly_cleaned_data_1972_2010.csv',
         'output_data/assembly_cleaned_data_2011_2012.csv',
         'post2013_scraper/post2013_state_legislative_elections.csv']

dfs = [pd.read_csv(f, dtype='object') for f in files]

all = pd.concat(dfs)

def clean_district_text(x):
    if isinstance(x, str) and re.match('^District ', x):
        return x.replace('District ', '')
    else:
        return x
        
all['District'] = all['District'].apply(clean_district_text)

all = all.sort_values(['State', 'Year', 'District']) # should also try natsorting the districts

all.to_csv('state_legislative_election_results_post1971.csv', index=False)