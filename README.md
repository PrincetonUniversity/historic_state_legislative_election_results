# State Legislative Elections,  1971 - 2017

This repo contains results of general elections to the lower house of the state legislatures over the last five decades, from 1971 to 2017.
Candidate information from Carl Klarner's [State Legislative Election Returns dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=hdl:1902.1/20401)
was used to compile these election results from 1971 - 2012. For each state, we only extract elections using Single Member districts (see below).

The elections dataset can be found in the output_data folder.

Analysis for elections up to 2012 (inclusive) can be re-run using the script main.py. Analysis for 2013-2017 elections can be re-run with post2013_scraper/run_scraper.py

This script and accompanying dataset are provided by the [Princeton Gerrymandering Project](http://gerrymander.princeton.edu/). Please
direct any feedback or questions to Brian Remlinger, brem at princeton dot edu. 
Although we have attempted to check the dataset for errors, accuracy cannot be guaranteed. 


This dataset is distributed under a [CC0 license](https://creativecommons.org/publicdomain/zero/1.0/), while the generator scripts are distributed under a [GNU GPL license](https://www.gnu.org/licenses/gpl-3.0.en.html). If you use this data for research or projects, we'd love to know! Please send along an email describing your work.

## Analysis Details
### Input data
Input data for 1971 - 2012 is drawn from Carl Klarner's SLER 1967 - 2010 dataset, as well as its [2011-2012 extension](https://dataverse.harvard.edu/dataset.xhtml?persistentId=hdl:1902.1/21549). Some precalculation was done on the 2011-2012 extension; see the Excel file in input_data.

Input data from 2013 - 2016 are Ballotpedia's state assembly election results pages. These pages are scraped using BeautifulSoup, then combined into a single file.

2016 NJ Assembly results are pulled from Ballotpedia. Because the districts are multimember, candidates from each party have been summed together.
2017 VA House of Delegates election results are pulled from the Virginia Department of Elections.

### Output dataset details
Each row of the output csv file represents an election. n 2013-2017 elections, the party winning the election is identified as Republican, Democrat,
Independent, Other, or Both. For details on how parties are designated in previous elections, see the codebook accompanying the SLER dataset. "Both" 
refers to races won by a candidate nominated by both major parties. For winning candidates nominated by a major party and a minor
party, only their major party is identified. Party vote totals represent the total number of votes received by each party in 
an election, even if they were split between several candidates.

In some elections, the number of votes cast was not recorded. The vast majority of these elections were uncontested races
in Florida, Oklahoma, or other states where candidates in unopposed races did not or do not appear on the ballot. In these 
cases, the winning party is assigned 100 votes and all other vote categories are assigned 0 votes.

"-1" in the incumbency column indicates that incumbency is not coded for those elections

In uncontested races from 2013 - 2016, the uncontested candidate is listed as receiving 1 vote when vote totals are not provided.

### Data Extraction Details

#### Elections excluded from dataset
Several elections are excluded from the dataset. In particular, Georgia's 2002 election is excluded because it used 
multi-member districts, and several elections Massachusetts and Maine in the 1970s are excluded because they preceded a large
change in the legislature size. Excluded elections can be found in elections_to_exclude.csv in the input_data folder.

#### Data modifications 
In several states in the 2011-2012 dataset extension, some candidates ran as candidates for both parties 
but operated and identified as members of one party. These candidates
are re-coded with the appropriate party ID 
in SLERs2011_2012_recoding.csv in the input_data folder.

#### First election using Single Member Districts, State By State

The trend in state legislative elections has been a move from multimember districts to single member districts, motivated in large part by the Voting Rights Act. The only exception to this is Georgia, which switched from single member to multimember districts in 2002, but was forced to switch back to single member districts by court order for the 2004 election.

##### States that switched from multimember districts to single member districts before 1972
##### Parenthetical is first election using single-member districts

California (pre- 1960)  
Delaware (pre- 1960)  
Kansas (pre- 1960)  
Kentucky (pre- 1960)   
Missouri (pre- 1960)  
New York (pre- 1960)  
Utah (pre- 1960)  
Wisconsin (pre- 1960)  
Michigan (1964)  
Oklahoma (1964)  
Connecticut (1966)  
New Mexico (1966)  
Pennsylvania (1966)  
Rhode Island (1966)  
Ohio (1966)  
Colorado (1968)  
Iowa (1968)  
Louisiana (1971)  
Massachusetts (1972)  
Minnesota (1972)  
Nevada (1972)  
Oregon (1972)  
Tennessee (1972)  

##### States that switched from multimember districts to single member districts between 1974 and 1985
##### Parenthetical is first election using single-member districts
Montana (1974)  
South Carolina (1974)  
Alabama (1974)  
Texas (1976)  
Maine (1976)  
Mississippi (1979)  
Arkansas (1982) [still had 1 multimember district until at least 2002, but removed most MMDs before 1982 election]  
Florida (1982)  
Hawaii (1982)  
Illinois (1982)  
Virginia (1984)  

##### States that switched from multimember districts to single member districts after 1985
Alaska (switched for 1992 election)  
Georgia (switched to SMD for 1992 election; switched back to MMD in 2002 election, but reverted to SMD for 2004)  
Indiana (switched for 1992 election)  
Wyoming (switched for 1992 election)  
North Carolina (switched for 2002 election)  

##### States still using multimember districts
Arizona   
Idaho   
Maryland    
New Hampshire  
New Jersey (New Jersey 2013, 2015, 2017 elections are included in this dataset)  
North Dakota  
South Dakota  
Vermont  
Washington (Washington 2014 and 2016 elections are included in this dataset)  
West Virginia  

##### Sources:
[The Impact of Multimember Districts on Party Representation in U. S. State Legislatures](http://www.jstor.org/stable/440068?seq=1#page_scan_tab_contents), Richard G. Niemi, Jeffrey S. Hill and Bernard Grofman, Legislative Studies Quarterly, Vol. 10, No. 4 (Nov., 1985), pp. 441-455

[Chapter 5: Multimember Districts](https://www.senate.mn/departments/scr/REDIST/Red2000/ch4multi.htm), Redistricting Law 2000, National Conference of State Legislatures

[Chapter 8 Multimember Districts](http://www.ncsl.org/Portals/1/Documents/Redistricting/Redistricting_2010.pdf), Redistricting Law 2010, National Conference of State Legislatures

[Ballotpedia](https://ballotpedia.org/Main_Page)
