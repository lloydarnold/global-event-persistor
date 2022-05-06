from flask import Flask, jsonify
from flask_cors import CORS
import sys
import optparse
import time
import json
from flask import request
import numpy as np
import sys
import os
import logging
import configparser
import requests

app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
CORS(app)
start = int(round(time.time()))

config = configparser.RawConfigParser()
config.read(filenames = './handler_config')

debug = bool(config.getint('general', 'DEBUG'))

classification_url = config.get('inference', 'CLASSIFICATION_URL')
sentiment_url = config.get('inference', 'SENTIMENT_URL')

db_endpoint = config.get('database', 'DB_ENDPOINT')

def get_sentiment(texts):
    js = { 'texts': texts }
    res = requests.post(sentiment_url, json = js)
    return res.json()['ans']

def find_date(news):
    possible_dates = [news['date_publish'], news['date_modify'], news['date_download']]
    non_null_dates = [x for x in possible_dates if x not in ["NULL", None]]
    if len(non_null_dates) > 0:
        return non_null_dates[0]
    else:
        return None

def make_event(news, sentiment, category):
    if debug:
        news_for_printing = dict(news)
        news_for_printing['maintext'] = news_for_printing['maintext'][:50]
        logging.info(json.dumps(news_for_printing, indent = 4))
    delta_sent = 100*(sentiment[0] - sentiment[1])
    
    event = {
        "timeStamp": find_date(news),
        "positivity": delta_sent,
        "source": news['url'],
        "category": category,
        "detail": news['title_page'],
        "eventRegions": []
    }
    if debug:
        logging.info(json.dumps(event, indent = 4))
    return event

def db_push(events):
    res = requests.post(db_endpoint, json = events)
    logger.info("Events pushed with response {}".format(res.status_code))
    if debug:
        js = json.loads(res.text)
        logger.info(json.dumps(js, indent = 4))
    return res.text

@app.route("/push_events", methods=['POST'])
def push_to_db():
    logging.info("Received request")
    res = request.get_json()
    articles = res['texts']
    category = res['category']

    titles = [x['title'] for x in articles]

    sents = get_sentiment(titles)

    events = [
        make_event(articles[i], sents[i], category)
        for i in range(0, len(titles))
    ]

    created_events = db_push(events)

    return {"res": created_events}
