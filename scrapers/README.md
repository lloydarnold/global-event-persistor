# Scrapers

We developed scrapers for GDELT, Twitter and Coinmarketcap News. Here is how they work:

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


