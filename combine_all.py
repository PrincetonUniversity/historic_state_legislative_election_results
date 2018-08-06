import pandas as pd
import re

files = ['output_data/assembly_cleaned_data_1972_2010.csv',
         'output_data/assembly_cleaned_data_2011_2012.csv',
         'post2013_scraper/post2013_state_legislative_elections.csv']

dfs = [pd.read_csv(f, dtype='object') for f in files]

all = pd.concat(dfs)


def clean_district_text(x):
    if isinstance(x, str) and re.match('^District ', x):
        return x.replace('District ', '').strip()
    else:
        return x.strip()
        
def district_no_for_sorting(x):
    x = re.sub('\D', '', x)
    if x=='':
        return 0
    else:
        return int(x)

all['District'] = all['District'].apply(clean_district_text)

sortname = 'District_for_sorting'
all[sortname] = all['District'].apply(district_no_for_sorting)
all = all.sort_values(['Year', 'State', sortname])

all['Dem Votes'] = all['Dem Votes'].apply(float).apply(int)
all['GOP Votes'] = all['GOP Votes'].apply(float).apply(int)
all['D Voteshare'] = all['Dem Votes'] / (all['Dem Votes'] + all['GOP Votes'])

all[[c for c in all.columns if c != sortname]].to_csv('state_legislative_election_results_post1971.csv', index=False)

