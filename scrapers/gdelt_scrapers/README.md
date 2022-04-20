# Scrapers Setup

A virtual environment is set up with all packages set up in scravervenv/

To activate the virtual environment:
- For windows ```scrapervenv\Scripts\activate```
- For bash/mac ```source scrapervenv/Scripts/activate```

To deactivate the virtual environment ```deactivate```

# livescraper.py Setup

You will need the inference API in language_models running and the backend running for this code to run. 

# filter.txt format

Change filter.txt to alter what data you are filtering in. Current example usage:  
'  
2000-01-01,2030-01-01  
-1000,1000  
-100,100  
<br/>
World,Sci/Tech  
<br/>
<br/>
KYIV/POLAND,RUSSIA  
<br/>
RS,UP/US  
'  
The first line contains start and end date (these are both inclusive).  
The second and third lines contain lower and upper bounds for positivity and relevance respectively.  
The fifth line is for filtering based on categories, separate the categories by commas. It will only include entries that have one of the listed categories.  
The blank lines are all placeholders for adding in filters based on URL for example. Note that these filters have not been coded in yet.
The eighth and tenth line are for actors and country codes. The format is to use a '/' for an OR, and a ',' for an AND. For example, 'KYIV/POLAND,RUSSIA' refers to (KYIV OR POLAND) AND RUSSIA.
