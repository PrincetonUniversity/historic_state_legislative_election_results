# State Legislative Elections,  1971 - 2012

This repo contains results of general elections to the lower house of the state legislatures over the last fifty years, up to 2012.
Candidate information from Carl Klarner's [State Legislative Election Returns dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=hdl:1902.1/20401)
was used to compile these election results. For each state, we only extract elections using Single Member districts (see below).

The elections dataset can be found in the output_data folder.

Analysis can be re-run using the script main.py.

This script and accompanying dataset are provided by the [Princeton Gerrymandering Project](http://gerrymander.princeton.edu/). Please
direct any feedback or questions to Brian Remlinger, brem at princeton dot edu. 
Although we have attempted to check the dataset for errors, accuracy cannot be guaranteed. 

## Analysis Details
### Input data
Input data is drawn from Carl Klarner's SLER 1967 - 2010 dataset, as well as its [2011-2012 extension](https://dataverse.harvard.edu/dataset.xhtml?persistentId=hdl:1902.1/21549). Some precalculation was done on the 2011-2012 extension; see the Excel file in input_data.

### Output dataset details
Each row of the output csv file represents an election. The party winning the election is identified as Republican, Democrat,
Independent, Other, or Both. For details on how parties are designated, see the codebook accompanying the SLER dataset. "Both" 
refers to races won by a candidate nominated by both major parties. For winning candidates nominated by a major party and a minor
party, only their major party is identified. Party vote totals represent the total number of votes received by each party in 
an election, even if they were split between several candidates.

In some elections, the number of votes cast was not recorded. The vast majority of these elections were uncontested races
in Florida, Oklahoma, or other states where candidates in unopposed races did not or do not appear on the ballot. In these 
cases, the winning party is assigned 100 votes and all other vote categories are assigned 0 votes.

### Data Extraction Details

#### Elections excluded from dataset
Several elections are excluded from the dataset. In particular, Georgia's 2002 election is excluded because it used 
multi-member districts, and several elections Massachusetts and Maine in the 1970s are excluded because they preceded a large
change in the legislature size. Excluded elections can be found in elections_to_exclude.csv in the input_data folder.

#### Data corrections
In several states in the 2011-2012 dataset extension, some candidates were marked as running under both parties, where
they in fact ran only on one party's platform. These errors are corrected in SLERs2011_2012_corrections.csv in the input_data folder.

#### First election using Single Member Districts, State By State
##### States that eliminated Multimember districts before 1960
California
Delaware
Kansas
Kentucky
Missouri
New York
Utah
Wisconsin

##### States that eliminated Multimember districts between 1960 and 1972
Parenthetical is first election using single-member districts
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

##### States that eliminated Multimember districts between 1974 and 1985
Parenthetical is first election using single-member districts
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

##### States using multimember districts after 1985
Alaska (switched for 1992 election)
Georgia (switched to SMD for 1992 election; switched back to MMD in 2002 election, but reverted to SMD for 2004)
Indiana (switched for 1992 election)
Wyoming (switched for 1992 election)
North Carolina (switched for 2002 election)

##### States using multimember districts after 2010
Arizona
Idaho
Maryland
New Hampshire
New Jersey
North Dakota
South Dakota
Vermont
Washington
West Virginia

##### Sources:
[The Impact of Multimember Districts on Party Representation in U. S. State Legislatures](http://www.jstor.org/stable/440068?seq=1#page_scan_tab_contents), Richard G. Niemi, Jeffrey S. Hill and Bernard Grofman, Legislative Studies Quarterly, Vol. 10, No. 4 (Nov., 1985), pp. 441-455

[Chapter 5: Multimember Districts](https://www.senate.mn/departments/scr/REDIST/Red2000/ch4multi.htm), Redistricting Law 2000, National Conference of State Legislatures

[Chapter 8 Multimember Districts](http://www.ncsl.org/Portals/1/Documents/Redistricting/Redistricting_2010.pdf), Redistricting Law 2010, National Conference of State Legislatures

