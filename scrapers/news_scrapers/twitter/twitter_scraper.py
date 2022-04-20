# Imoprts
from socket import timeout
from newsplease import NewsPlease
import requests
from bs4 import BeautifulSoup
import unidecode
import json
import re
import numpy as np 
import configparser
import datetime
import logging

logger = logging.basicConfig(filename = "./twitter_scraper.log", format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

config = configparser.RawConfigParser()
config.read(filenames = './scraper_config')
config.read(filenames = '.env')
config.read(filenames = '.env.secret')

debug = bool(config.getint('general', 'DEBUG'))

source_url = config.get('acquisition', 'SOURCE_URL')
num_tweets = config.getint('acquisition', 'NUM_TWEETS')
datetime_format = config.get('acquisition', 'DATETIME_FORMAT')

classification_url = config.get('inference', 'CLASSIFICATION_URL')
sentiment_url = config.get('inference', 'SENTIMENT_URL')

db_endpoint = config.get('database', 'DB_ENDPOINT')

access_token = config.get('twitter-api-private', 'ACCESS_TOKEN')
access_token_secret = config.get('twitter-api-private', 'ACCESS_TOKEN_SECRET')
api_key = config.get('twitter-api', 'API_KEY')
api_secret_key = config.get('twitter-api', 'API_SECRET_KEY')
bearer_token = config.get('twitter-api', 'BEARER_TOKEN')

search_words = json.loads(config.get('query', 'SEARCH_WORDS'))
language = config.get('query', 'LANGUAGE')
retweets = bool(config.getint('query', 'RETWEETS'))

category = config.get('general', 'CATEGORY')

timestamp = datetime.datetime.now()

def bearer_oauth(r):
    r.headers["Authorization"] = "Bearer {}".format(bearer_token)
    r.headers["User-Agent"] = 'v2RecentSearchPython'
    return r

def connect_to_endpoint(url, params):
    res = requests.get(url, auth = bearer_oauth, params = params)
    print(res.status_code)
    if res.status_code != 200:
        raise Exception(res.status_code, res.text)
    return res.json()

def get_tweets(query_params):
    res = connect_to_endpoint(source_url, query_params)
    if debug:
        logger.info(res['data'][:5])
    data = res['data']
    print(len(data))
    return data

def make_query():
    if debug:
        logger.info(search_words)

    query = " ".join(search_words)
    if language != "":
        query = query + f" lang:{language}"
    if not retweets:
        query = query + " -is:retweet"
    
    query_params = {
        "query": query,
        "max_results": num_tweets
    }

    if debug:
        logger.info(query_params)

    return query_params


def get_sentiment(texts):
    js = { 'texts': texts }
    res = requests.post(sentiment_url, json = js)
    return res.json()['ans']

def db_push(events):
    res = requests.post(db_endpoint, json = events)
    logger.info("Events pushed with response {}".format(res.status_code))
    if debug:
        logger.info(res.text)

if __name__ == '__main__':
    print(db_endpoint)
    query_params = make_query()
    tweet_data = get_tweets(query_params=query_params)
    texts = [tweet['text'] for tweet in tweet_data]
    sentiments = get_sentiment(texts)

    assert(len(tweet_data) == len(texts) and len(texts) == len(sentiments))

    sentiments = np.array(sentiments)
    delta_sent_avg = 100 * np.mean(sentiments[:, 0] - sentiments[:, 1])

    str_timestamp = timestamp.strftime(datetime_format)

    event = {
        "timeStamp": str_timestamp,
        "positivity": delta_sent_avg,
        "source": "Twitter",
        "category": "FIN",
        "detail": "Average sentiment of tweets for " + "; ".join(search_words) + " at " + str_timestamp,
        "actors": search_words,
        "stocks": search_words,
        "eventRegions": []
    }
    
    db_push([event])
