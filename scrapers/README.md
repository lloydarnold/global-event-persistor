# Scrapers

We developed scrapers for GDELT, Twitter and Coinmarketcap News. Here is how they work:

## Scrapers Setup

A virtual environment is set up with all packages set up in scravervenv/

To activate the virtual environment:
- For windows ```scrapervenv\Scripts\activate```
- For bash/mac ```source scrapervenv/Scripts/activate```

To deactivate the virtual environment ```deactivate```

## Coinmarketcap Scraper

This scraper gets news directly from Coinmarketcap's News API. It provides news from various Crypto assets, and tags each article with the relevant assets. The scraper also provides a sentiment tag for the headline of news articles, which is obtained using FinBERT, a BERT model finetuned for estimating the sentiment of financial news headlines.

### Configurations
The scraper comes with a `scraper_config` file. Its fields are:

```
[general]
DEBUG: set to 1 for logging extra information when running the scraper

[acquisition]
SOURCE_URL: endpoint of the Coinmarketcap news API
PAGE_SIZE: number of articles per page to be queried from the API
NUM_ARTICLES: total number of articles to be queried in 1 run of the script
DATETIME_FORMAT: format in which to put the timestamp for the publication of the article

[inference]
CLASSIFICATION_URL: endpoint for classifying the news article. Currently not used in the scraper
SENTIMENT_URL: endpoint for sentiment tagging of article headlines

[database]
DB_ENDPOINT: endpoint for creating multiple events in the database (whose code is in the `backend` folder)
```

### Usage

One run of the scraper does one round of scraping data from Coinmarketcap. The script is intended to be used as a cronjob configured to run periodically. At each round of scraping, one event is pushed to the database for each retrieved article. The fields of the event record are filled as follows:

```
timeStamp: timestamp of publication of the article
positivity: 100 * (p - n), where p and n are the negative and positive sentiments returned by the sentiment analysis API
source: link of the original news article
detail: title of the article
stocks: assets associated with the article; provided directly by the Coinmarketcap API
actors: also contains the assets involved
eventRegions: left blank
```

To set up for the first time, the right conda environment for the scraper needs to be created:
```
cd scrapers/news_scrapers
conda env create -f environment.yml
```

Once this is done, the environment must be activated before running:

```
conda activate scraperenv
python coinmarketcap_scraper.py
```

Notice that the inference API and the Backend also need to be running (or deployed remotely), with the appropriate URLs in the configuration file.

Logs are written to `coinmarketcap_scraper.log`.


## Twitter Scraper

This scraper gets recent tweets from Twitter's official API, and creates an event summarizing their sentiment using TweetBERT, a BERT model finetuned for sentiment analysis of tweets. Thus, this should be used to scrape tweets from a single topic or a handful of similar ones;.

### Configurations
The scraper comes with a `scraper_config` file. Its fields are:

```
[general]
DEBUG: set to 1 for logging extra information when running the scraper
CATEGORY: category of the event to be created in the database. This should reflect whether one is scraping financial events, sports events, and etc.

[acquisition]
SOURCE_URL: endpoint of the search endpoint of the Twitter v2 
NUM_tweet: number of tweets to be pulled. Max is 100.
DATETIME_FORMAT: format in which to put the timestamp for the publication of the article

[query]
SEARCH_WORDS: keywords to search for on tweets. Can include hashtags.
LANGUAGE: Language of the tweets. Default is en, as the sentiment classifier assumes the tweets are in English.
RETWEETS: 1 to allow retweets; 0 to scrape only original tweets

[inference]
CLASSIFICATION_URL: endpoint for classifying the tweet. Currently not used in the scraper
SENTIMENT_URL: endpoint for sentiment tagging of tweets. It supports emojis.

[database]
DB_ENDPOINT: endpoint for creating multiple events in the database (whose code is in the `backend` folder)
```

The Twitter API requires additional configurations relating to authentication. These are included in hidden `.env` and `.env.secret` files, as they contain keys that give access to one's Twitter account. For details on these see the official Twitter API documentation.

`.env`:
```
[twitter-api]
API_KEY = xxxxx
API_SECRET_KEY = xxxxxx
BEARER_TOKEN = xxxxx
```

`.env.secret`:
```
[twitter-api-private]
ACCESS_TOKEN = xxxxx
ACCESS_TOKEN_SECRET = xxxxx
```

### Usage

One run of the scraper does one round of scraping tweets. The script is intended to be used as a cronjob configured to run periodically. At each round of scraping, a single event summarizing the scraped tweets is pushed to the database. The fields of the event record are filled as follows:

```
timeStamp: timestamp of the run of the scraper
positivity: 100 * (p - n), where p and n are the negative and positive sentiments returned by the sentiment analysis API
source: "Twitter"
detail: "Average sentiment of tweets for <search words> at <timestamp>"
stocks: search words used to query the tweets
actors: search words used to query the tweets
eventRegions: left blank
```

To set up for the first time, the right conda environment for the scraper needs to be created:
```
cd scrapers/news_scrapers
conda env create -f environment.yml
```

Once this is done, the environment must be activated before running:

```
conda activate scraperenv
python twitter_scraper.py
```

Notice that the inference API and the Backend also need to be running (or deployed remotely), with the appropriate URLs in the configuration file.

Logs are written to `twitter_scraper.log`.

## GDELT Scrapers:

You will need the inference API in language_models running and the backend running for these gdelt scrapers to run (this API classifies entries into categories).

### Configuration

scutility.py is used to interact with the inference API, so this file must be in scrapers/gdelt_scrapers. When running the inference API, it will state which url it is sending the data to, and so the variable `url` in scutility.py must be changed to this url. 

## GDELT Query

This scraper will fetch all entries satisfying the query given in the GDELT database and add these to the database using Google BigQuery. Additionally, it utilises an inference API (in language_models) that classifies the categeory of the event based on the source URL.

### Configuration

Google BigQuery needs to be setup to run this code. A Google BigQuery account will be required, then follow the section "setting up authentication" in the following link https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python to get a service account file json. Call this file 'service-account-file.json' and include this in scrapers/gdelt_scrapers.  
<br/>
query.txt will be used as the query sent to Google BigQuery. Google BigQuery supports standard SQL and legacy SQL. Example for query.txt:

```
SELECT *
FROM `gdelt-bq.full.events`
WHERE
(Actor1CountryCode = 'GBR'
OR Actor1Geo_Fullname = 'United Kingdom'
OR Actor2Geo_CountryCode = 'UK')
AND Year = 2010
LIMIT 1
```

### Usage

```
cd scrapers/gdelt_scrapers
python historicalscraper.py
```

## Daily GDELT Scraper

Running this code will find all entries that satisfy the conditions given in filter.txt (format explained below) and add them to the specified database in the backend from the most recent csv at http://data.gdeltproject.org/events/index.html. This scraper will be ran daily (could be ran more or less frequently) to scrape from the most recently added data to GDELT and add entries to the database.

### Configuration

filter.txt needs to be setup so that only certain data is added to the database:

#### filter.txt format

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

### Usage

```
cd scrapers/gdelt_scrapers
python livescraper.py
```



