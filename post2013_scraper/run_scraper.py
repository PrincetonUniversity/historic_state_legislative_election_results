from results_2013_2014.state_legislature_scrape_2013_2014 import scrape_results as sr1314
from results_2015.state_legislature_scrape_2015 import scrape_results as sr15
from results_2016.state_legislature_scrape_2016 import scrape_results as sr16
from results_2016.state_legislature_scrape_2016_ny import scrape_results as sr16_ny
from results_2017.state_legislature_scrape_2017 import scrape_results as sr17

import pandas as pd
import json

if __name__ == '__main__':

    #files containing web scraper outputs, used as inputs to create election information file
    outfile_2013_2014 = 'results_2013_2014/election_results_2013_2014.csv' 
    outfile_2015 = 'results_2015/2015_election_results.csv'
    outfile_2016 = 'results_2016/2016_election_results.csv'
    outfile_2016_ny = 'results_2016/2016_election_results_ny.csv'
    outfile_2017_nj = 'results_2017/nj2017.csv'
    outfile_2017_va = 'results_2017/va2017.csv'

    #toggle to re-scrape the results from ballotpedia. If false,
    #intermediate data files (results of web-scraping) are used
    #to create election information file
    rescrape = False

    if rescrape:
        #scripts to run web scrapes for the various years. url_file_xxx contains
        #the webpage urls. See year directories for details

        url_file_2013_2014 = 'results_2013_2014/2013_2014_urls.csv' 
        race_results_2013_2014 = sr1314(url_file_2013_2014, outfile_2013_2014)
        
        url_file_2015 = 'results_2015/2015_urls.csv'
        race_results_2015 = sr15(url_file_2015, outfile_2015)
        
        url_file_2016 = 'results_2016/2016_urls.csv'
        race_results_2016 = sr16(url_file_2016, outfile_2016)
        
        #new york 2016 was formatted differently than the other 2016 results years,
        #so has a seperate scraping script
        url_file_2016_ny = 'results_2016/2016_urls_ny.csv'
        race_results_2016_ny = sr16_ny(url_file_2016_ny, outfile_2016_ny)

        url_file_2017 = 'results_2017/2017_urls.csv'
        race_results_2017 = sr17(outfile_2017_nj, outfile_2017_va)

    #state name -> abbreviation dictionary file
    states = json.load(open('name_to_abbrev.json'))

    #file where the election info will be saved
    all_elections_outfile = 'post2013_state_legislative_elections.csv'
    #%%
    dfs_old_style = [pd.read_csv(x) for x in [outfile_2013_2014, outfile_2015, outfile_2016_ny]] + \
                    [pd.read_csv(outfile_2017_nj, header=None, names=['Year', 'State', 'District', 'Party', 'Name', 'Votes', 'Winner', 'Incumbent'])]
    
    dfs_new_style = [pd.read_csv(x) for x in [outfile_2016, outfile_2017_va]]
    
    all = pd.DataFrame()
    
    for df in dfs_old_style:
        df['Party'] = df['Party'].fillna('')
        
        df.loc[df['Party'].apply(lambda x: x.find('Dem') != -1), 'Party'] = 'Dem'
        df.loc[df['Party'].apply(lambda x: x.find('GOP') != -1), 'Party'] = 'GOP'
        df.loc[df['Party'].apply(lambda x: x.find('Repub') != -1), 'Party'] = 'GOP'
        df.loc[~df['Party'].isin(['Dem', 'GOP']), 'Party'] = 'Other'
        
        
        # drop and merge duplicates
        cols = ['Year', 'State', 'District', 'Name']
        
        df = df.drop_duplicates(subset=cols + ['Party'])
        
        dupes = df[df.duplicated(subset=cols, keep=False)].sort_values(cols + ['Party'])
        
        if len(dupes) > 1:
            old_id = dupes.iloc[0].name
            old = dupes.iloc[0]
            
            # take care of candidates running under multiple parties
            for new_id, new in dupes[1:].iterrows():
                if (new[cols] == old[cols]).all():
                    df.loc[old_id, 'Votes'] += df.loc[new_id, 'Votes']
                    df = df.drop(new_id)
                else:
                    old_id = new_id
                    old = new
        
        piv = df.pivot_table(values=['Votes', 'Incumbent'], index=['State', 'Year', 'District'], columns='Party')

        D_inc = (piv['Incumbent']['Dem']==1) & (piv['Incumbent']['GOP']!=1) & (piv['Incumbent']['Other']!=1)
        R_inc = (piv['Incumbent']['Dem']!=1) & (piv['Incumbent']['GOP']==1) & (piv['Incumbent']['Other']!=1)
        I_inc = (piv['Incumbent']['Dem']!=1) & (piv['Incumbent']['GOP']!=1) & (piv['Incumbent']['Other']==1)
        no_inc = (piv['Incumbent']['Dem']!=1) & (piv['Incumbent']['GOP']!=1) & (piv['Incumbent']['Other']!=1)
        piv.loc[D_inc, 'Inc'] = 'D'
        piv.loc[R_inc, 'Inc'] = 'R'
        piv.loc[I_inc, 'Inc'] = 'I'
        piv.loc[no_inc, 'Inc'] = 'O'

        piv = piv.drop(columns='Incumbent')

        piv.columns = [' '.join(col).strip() for col in piv.columns.values]
            
        piv = piv.reset_index()

        piv = piv.rename(columns={'Votes Dem': 'Dem Votes', 'Votes GOP': 'GOP Votes', 'Votes Other': 'Other Votes', 'Inc': 'Incumbent'})
        
        all = pd.concat([all, piv])
    
    
    def convert_string(x):
        if x=='True' or x=='1' or x==1 or x==True:
            return True
        else:
            return False    
    
    for df in dfs_new_style:
        df['Other Incumbent'] = df['Other Incumbent'].apply(convert_string)
        
        D_inc = df['Democrat Incumbent'] & ~df['Republican Incumbent'] & ~df['Other Incumbent']
        R_inc = ~df['Democrat Incumbent'] & df['Republican Incumbent'] & ~df['Other Incumbent']
        I_inc = ~df['Democrat Incumbent'] & ~df['Republican Incumbent'] & df['Other Incumbent']
        no_inc = ~df['Democrat Incumbent'] & ~df['Republican Incumbent'] & ~df['Other Incumbent']

        df.loc[D_inc, 'Incumbent'] = 'D'
        df.loc[R_inc, 'Incumbent'] = 'R'
        df.loc[I_inc, 'Incumbent'] = 'I'
        df.loc[no_inc, 'Incumbent'] = 'O'

        df = df[['State', 'District', 'Year', 'Incumbent', 'Democrat Votes', 'Republican Votes', 'Other Votes']]
        
        df = df.rename(columns={'Democrat Votes': 'Dem Votes', 'Republican Votes': 'GOP Votes'})
    
        all = pd.concat([all, df])
        
    
    fill = ['Dem Votes', 'GOP Votes', 'Other Votes']
    all[fill] = all[fill].fillna(0)

    all['State'] = all['State'].apply(lambda x: states[x])
    all['District'] = all['District'].apply(lambda x: str(x).replace('District ', '').strip())


    D_winner = (all['Dem Votes'] > all['GOP Votes']) & (all['Dem Votes'] > all['Other Votes'])
    R_winner = (all['GOP Votes'] > all['Dem Votes']) & (all['GOP Votes'] > all['Other Votes'])
    I_winner = (all['Other Votes'] > all['Dem Votes']) & (all['Other Votes'] > all['GOP Votes'])
    all.loc[D_winner, 'Party'] = 'D'
    all.loc[R_winner, 'Party'] = 'R'
    all.loc[I_winner, 'Party'] = 'I'
    
    all = all[['State', 'District', 'Year', 'Party', 'Incumbent', 'Dem Votes', 'GOP Votes', 'Other Votes']].sort_values(['Year', 'State', 'District'])

    all.to_csv('post2013_state_legislative_elections.csv', index=False)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    