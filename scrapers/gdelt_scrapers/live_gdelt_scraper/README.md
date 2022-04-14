Change filter.txt to alter what data you are filtering in. Current example usage:
'
2000-01-01,2030-01-01
-1000,1000
-100,100




KYIV/POLAND,RUSSIA

RS,UP/US
'
The first line contains start and end date (these are both inclusive).
The second and third lines contain lower and upper bounds for positivity and relevance respectively.
The blank lines are all placeholders for adding in filters based on URL for example. Note that these filters have not been coded in yet.
The eighth and tenth line are for actors and country codes. The format is to use a '/' for an OR, and a ',' for an AND. For example, 'KYIV/POLAND,RUSSIA' refers to (KYIV OR POLAND) AND RUSSIA.

Note that some forms of verification should still be done. For example if the first line of this txt is empty, it should be the case that all dates are considered.
