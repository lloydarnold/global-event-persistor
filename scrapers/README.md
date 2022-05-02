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

You will need the inference API in language_models running and the backend running for these gdelt scrapers to run (this API classifies entries into categories). Also these scrapers use a fake news classification model (`gdelt_scrapers_config/fake_news_classification/saved_weights.pt` is the saved model). GDELT currently stores global locations using the FIPS code system, but doesn't use FIPS for American locations. Changing whether these scrapers use FIPS or not should only be done if GDELT changes their format of locations.

### Configuration

`scutility.py` is used to interact with the inference API, so this file must be in scrapers/gdelt_scrapers. This comes with a `scutility_config` which has the following field:

```
[inference]
CLASSIFICATION_URL: the endpoint for the classification section of the inference API. http://127.0.0.1:8080/news-classification by default - need to check this when running the inference API
```

## GDELT Query

This scraper will fetch all entries satisfying the query given in the GDELT database and add these to the database using Google BigQuery. Additionally, it utilises an inference API (in language_models) that classifies the categeory of the event based on the source URL.

### Configuration

Google BigQuery needs to be setup to run this code. A Google BigQuery account will be required, then follow the section "setting up authentication" in the following link https://cloud.google.com/bigquery/docs/reference/libraries#client-libraries-install-python to get a service account file json. Call this file `service-account-file.json` and include this in scrapers/gdelt_scrapers.  
<br/>
This scraper comes with a `historical_config` file with the following fields:

```
[database]
DB_ENDPOINT: endpoint for sending multiple entries to. Use http://localhost:3000/events/create-many for local, http://3.82.122.96:3000/events/create-many is the current URL for our backend.
GLOBAL_IS_FIPS: 1 for FIPS, 0 for no FIPS.
AMERICA_IS_FIPS: 1 for FIPS, 0 for no FIPS.
ENTRIES_CAP: cap the number of entries being classified and sent to the database.
CATEGORY_CLASSIFY: true for category classification and false for no classification. Remove category based classification if processing large amounts of data is more important than the categories of that data.
NEWS_CLASSIFY: true for fake news classification and false for no classification. Note that not all events will contain whether it is fake news or not (this can depend on URLs that cannot be searched).

[google]
ACCOUNT_FILE: name of the service account file for Google BigQuery. service-account-file.json is the default.
GOOGLE_SCOPES: list of scopes for Google BigQuery. ["https://www.googleapis.com/auth/cloud-platform"] is the default.

[query]
QUERY_FILE: name of the file containing the query. query.txt by default.
```

`query.txt` will be used as the query sent to Google BigQuery. Google BigQuery supports standard SQL and legacy SQL. Example for `query.txt`:

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

The fields that can be queried about are below. For more information about these fields look at http://data.gdeltproject.org/documentation/GDELT-Event_Codebook-V2.0.pdf.
```
"GLOBALEVENTID",
"SQLDATE",
"MonthYear",
"Year",
"FractionDate",
"Actor1Code",
"Actor1Name",
"Actor1CountryCode",
"Actor1KnownGroupCode",
"Actor1EthnicCode",
"Actor1Religion1Code",
"Actor1Religion2Code",
"Actor1Type1Code",
"Actor1Type2Code",
"Actor1Type3Code",
"Actor2Code",
"Actor2Name",
"Actor2CountryCode",
"Actor2KnownGroupCode",
"Actor2EthnicCode",
"Actor2Religion1Code",
"Actor2Religion2Code",
"Actor2Type1Code",
"Actor2Type2Code",
"Actor2Type3Code",
"IsRootEvent",
"EventCode",
"EventBaseCode",
"EventRootCode",
"QuadClass",
"GoldsteinScale",
"NumMentions",
"NumSources",
"NumArticles",
"AvgTone",
"Actor1Geo_Type",
"Actor1Geo_FullName",
"Actor1Geo_CountryCode",
"Actor1Geo_ADM1Code",
"Actor1Geo_Lat",
"Actor1Geo_Long",
"Actor1Geo_FeatureID",
"Actor2Geo_Type",
"Actor2Geo_FullName",
"Actor2Geo_CountryCode",
"Actor2Geo_ADM1Code",
"Actor2Geo_Lat",
"Actor2Geo_Long",
"Actor2Geo_FeatureID",
"ActionGeo_Type",
"ActionGeo_FullName",
"ActionGeo_CountryCode",
"ActionGeo_ADM1Code",
"ActionGeo_Lat",
"ActionGeo_Long",
"ActionGeo_FeatureID",
"DATEADDED",
"SOURCEURL"
```

### Usage

In Anaconda:
```
cd scrapers/gdelt_scrapers
python historicalscraper.py
```

## Daily GDELT Scraper

Running this code will find all entries that satisfy the conditions given in `live_config` and add them to the database. This scraper will be ran daily (could be ran more or less frequently) to scrape from the most recently added data to GDELT and add entries to the database.

### Configuration

This scraper comes with a `live_config` file with the following fields:

```
[database]
DB_ENDPOINT: endpoint for sending multiple entries to. Use http://localhost:3000/events/create-many for local, http://3.82.122.96:3000/events/create-many is the current URL for our backend.
GLOBAL_IS_FIPS: 1 for FIPS, 0 for no FIPS.
AMERICA_IS_FIPS: 1 for FIPS, 0 for no FIPS.
ENTRIES_CAP: cap the number of entries being classified and sent to the database.
CATEGORY_CLASSIFY: true for category classification and false for no classification. Remove category based classification if processing large amounts of data is more important than the categories of that data.  
NEWS_CLASSIFY: true for fake news classification and false for no classification. Note that not all events will contain whether it is fake news or not (this can depend on URLs that cannot be searched).

[filter]
DATE_RANGE: filter entries by dates. [YYYY-MM-DD,YYYY-MM-DD] gives the from and to date of events to include (inclusive of both ends). Use [] for no filtering of dates.
POS_RANGE: filter entries by positivity. [x,y] gives the lower and upper bound for positivity (inclusive of both ends). Use [] for no filtering.
REL_RANGE: filter entries by relativitiy. [x,y] gives the lower and upper bound for relativity (inclusive of both ends). Use [] for no filtering.
CATEGORY_LIST: filter entries by category. Give a list of categories, only entries that have at least one of these categories will be added. Use [] for no filtering.
ACTOR_LIST: filter by actors. [[Caregiver, Washington],Poland] will only include entries that have (Caregiver or Washington) and Poland as their actors. Use [] for no filtering.
COUNTRY_LIST: filter by countries. Same format as ACTOR_LIST except this is restricted to country codes (FIPS is the current standard for GDELT).

[gdelt]
GDELT_URL: URL for the GDELT files. This is http://data.gdeltproject.org/events/ as of now.
GDELT_FILE: number of file to take from GDELT in order of date. 0 will retrieve the most recent file, 1 the next, etc.
```

### Usage

In Anaconda:
```
cd scrapers/gdelt_scrapers
python livescraper.py
```
