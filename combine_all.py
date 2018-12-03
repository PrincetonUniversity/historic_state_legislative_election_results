import pandas as pd
import re
import numpy as np

files = ['output_data/assembly_cleaned_data_1972_2010.csv',
         'output_data/assembly_cleaned_data_2011_2012.csv',
         'post2013_scraper/post2013_state_legislative_elections.csv',
         '2018_Statehouses_20181203.csv']

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
all['Dem Votes'] = all['Dem Votes'].apply(float).apply(int)
all['GOP Votes'] = all['GOP Votes'].apply(float).apply(int)

# various cleanup
find_row = lambda year, state, district: (all['Year']==str(year)) & (all['State']==state) & (all['District']==str(district))
all.loc[find_row(2017, 'VA', 94), ['Party', 'GOP Votes']] = ['R', int(all.loc[find_row(2017, 'VA', 94), 'Dem Votes'] + 1)] # tiebreaker
all.loc[find_row(2016, 'MN', '32B[6]'), ['Party', 'Dem Votes', 'GOP Votes']] = ['R', '3327', '3789'] # MN special
all.loc[find_row(2014, 'MN', '15B'), 'Incumbent'] = 'R'
all.loc[find_row(2014, 'DE', '33'), 'Incumbent'] = 'R'
all.loc[(all['Party']=='R') & (all['GOP Votes']==0), 'GOP Votes']=1 # missing vote values for uncontested races in 2012
all.loc[(all['Party']=='D') & (all['Dem Votes']==0), 'Dem Votes']=1

sortname = 'District_for_sorting'
all[sortname] = all['District'].apply(district_no_for_sorting)
all = all.sort_values(['Year', 'State', sortname])

all['D Voteshare'] = np.array(all['Dem Votes']).astype(float) / np.array(all['Dem Votes'] + all['GOP Votes']).astype(float)
all = all.fillna(0) # set 0/0 (usually I wins) to D voteshare=0
columns = ['State', 'Year', 'District', 'Dem Votes', 'GOP Votes', 'D Voteshare', 'Incumbent', 'Party']

all[columns].to_csv('state_legislative_election_results_post1971.csv', index=False)
