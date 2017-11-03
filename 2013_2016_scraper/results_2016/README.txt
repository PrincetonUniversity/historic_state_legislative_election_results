NY uses the old 2013-14 format, so that gets imported using a different script. There's some issue with "Democratic Primary candidates" and "Republican primary candidates" getting treated as candidates.

In California (and any other state that has two candidates from one party in the general) vote totals are wrong for the total number of Dem or Rep votes where 2 Dems or 2 Reps are running. This doesn't matter for analysis, since those races will show up as uncontested, but may be important for other uses.


2016_urls.csv contains the urls to the Ballotpedia 2016 state elctions results pages
state_legislature_scrape_2016.py does the scraping and writes the results to 2016_election_results.csv

files with _ny appended do the same thing, but for the special case of New York
