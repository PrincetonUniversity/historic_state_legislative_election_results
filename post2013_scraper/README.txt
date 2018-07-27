State legislative election data for 2013 - 2016 races was scraped from ballotpedia. The format of results pages changed from year to year,
necessitating several different scripts. All efforts have been taken to ensure the accuracy of results, but accuracy cannot be guaranteed.

In order to re-run the analysis, use run_scraper.py.

combine_results.py is a script that reads in the scraper outputs (rows of candidate information) and creates a csv file of election results (one election per row).

names_to_abbrev.json is a json file that maps full state names to their abbreviations (e.g. Alaska -> AK).
