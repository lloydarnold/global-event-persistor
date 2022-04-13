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

logger = logging.basicConfig(filename = "./coinmarketcap_scraper.log", format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

config = configparser.RawConfigParser()
config.read(filenames = './scraper_config')

debug = bool(config.getint('general', 'DEBUG'))

source_url = config.get('acquisition', 'SOURCE_URL')
page_size = config.getint('acquisition', 'PAGE_SIZE')
num_articles = config.getint('acquisition', 'NUM_ARTICLES')
datetime_format = config.get('acquisition', 'DATETIME_FORMAT')

classification_url = config.get('inference', 'CLASSIFICATION_URL')
sentiment_url = config.get('inference', 'SENTIMENT_URL')

db_endpoint = config.get('database', 'DB_ENDPOINT')

# Get news from Coinmarketcap
def get_news():
    num_pages = num_articles/page_size
    num_remaining = num_articles
    news_data = []
    page = 1

    while num_remaining > 0:
        to_get = min(num_remaining, 200)

        headers = {
            "page": str(page),
            "size": str(page_size)
        }

        res = requests.get(source_url, headers = headers)
        news_data += json.loads(res.text)['data']
        num_remaining -= to_get
        page += 1

    links = [news['meta']['sourceUrl'] for news in news_data]

    # url_data = [ v for k, v in NewsPlease.from_urls(links, timeout = 5).items() ]
    # print(json.dumps(url_data[0].get_serializable_dict(), indent = 1))
    # url_data = [ news.get_dict() for news in url_data ]

    final_data = []

    for i in range(len(news_data)):
        from_coinmarketcap = news_data[i]
        news = {
            'stocks': [asset['name'] for asset in from_coinmarketcap['assets']],
            'source': from_coinmarketcap['meta']['sourceName'],
            'detail': from_coinmarketcap['meta']['title'],
            'timestamp': from_coinmarketcap['meta']['releasedAt']
        }
        final_data.append(news)


    return final_data

def get_sentiment(texts):
    js = { 'texts': texts }
    res = requests.post(sentiment_url, json = js)
    return res.json()['ans']



def make_event(news, sentiment):
    delta_sent = 100*(sentiment[0] - sentiment[1])
    event = {
        "timeStamp": news['timestamp'],
        "positivity": delta_sent,
        "relevance": -1,
        "source": news['source'],
        "category": "FIN",
        "detail": news['detail'],
        "actors": news['stocks'],
        "stocks": news['stocks'],
        "eventRegions": []
    }
    return event

def db_push(events):
    res = requests.post(db_endpoint, json = events)
    logger.info("Events pushed with response {}".format(res.status_code))
    if debug:
        logger.info(res.text)

if __name__ == '__main__':
    print(db_endpoint)
    news_data = get_news()
    titles = [news['detail'] for news in news_data]
    sentiments = get_sentiment(titles)

    assert(len(news_data) == len(titles) and len(titles) == len(sentiments))

    events = []
    for i in range(0, len(titles)):
        events.append(make_event(news_data[i], sentiments[i]))
    
    db_push(events)
