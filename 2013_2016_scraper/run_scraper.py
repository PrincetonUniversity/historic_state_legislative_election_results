from results_2013_2014.state_legislature_scrape_2013_2014 import scrape_results as sr1314
from results_2015.state_legislature_scrape_2015 import scrape_results as sr15
from results_2016.state_legislature_scrape_2016 import scrape_results as sr16
from results_2016.state_legislature_scrape_2016_ny import scrape_results as sr16_ny
from results_2017.state_legislature_scrape_2017 import scrape_results as sr17
from combine_results import combine_results


if __name__ == '__main__':

    #files containing web scraper outputs, used as inputs to create election information file
    outfile_2013_2014 = 'results_2013_2014/election_results_2013_2014.csv' 
    outfile_2015 = 'results_2015/2015_election_results.csv'
    outfile_2016 = 'results_2016/2016_election_results.csv'
    outfile_2016_ny = 'results_2016/2016_election_results_ny.csv'
    outfile_2017 = 'results_2017/2017_election_results.csv'

    #toggle to re-scrape the results form ballotpedia. If false,
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
    race_results_2017 = sr17(url_file_2017, outfile_2017)

    #state name -> abbreviation dictionary file
    dict_file = 'name_to_abbrev.json'

    #file where the election info will be saved
    all_elections_outfile = '2013_2017_state_legislative_elections.csv'

    list_of_elections_files = [
                                outfile_2013_2014, 
                                outfile_2015, 
                                outfile_2016, 
                                outfile_2016_ny,
                                outfile_2017
                                ]
    
    #combine the candidate information from the various years into one election-information file
    elections_dict = combine_results(list_of_elections_files, dict_file, all_elections_outfile)
