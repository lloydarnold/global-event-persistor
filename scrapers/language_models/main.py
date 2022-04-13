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
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TFAutoModelForSequenceClassification
import tensorflow as tf
import logging

class FinBERT:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        # self.tokenizer = None # AutoTokenizer.from_pretrained("ProsusAI/finbert")
        # self.model = None # AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

class TweetBERT:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("rabindralamsal/finetuned-bertweet-sentiment-analysis")
        self.model = TFAutoModelForSequenceClassification.from_pretrained("rabindralamsal/finetuned-bertweet-sentiment-analysis")
        # self.tokenizer = None # AutoTokenizer.from_pretrained("ProsusAI/finbert")
        # self.model = None # AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

class NewsClassification:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("mrm8488/bert-mini-finetuned-age_news-classification")
        self.model = AutoModelForSequenceClassification.from_pretrained("mrm8488/bert-mini-finetuned-age_news-classification")
        self.id2label = {
            0: "World",
            1: "Sports",
            2: "Business",
            3: "Sci/Tech"
        }
        # self.tokenizer = None # AutoTokenizer.from_pretrained("ProsusAI/finbert")
        # self.model = None # AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")


app = Flask(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
CORS(app)
start = int(round(time.time()))
size = 20

def chunk(arr, size):
    n = len(arr)
    return [arr[i:min(i+size, n)] for i in range(0, n, size)]

@app.route("/finbert",methods=['POST'])
def score_fin():
    logger.info("Beginning to load FinBERT model")
    finbert = FinBERT()
    texts=request.get_json()['texts']
    preds = np.array([]).reshape((0, 3))
    num_chunks = (len(texts) + 1)//size
    for i, batch in enumerate(chunk(texts, size)):
        logger.info(f"Processed chunk {i} out of {num_chunks}")
        input = finbert.tokenizer(batch, return_tensors="pt", padding = True)
        output = finbert.model(**input).logits.cpu().detach()
        # print(output)
        preds = np.concatenate((preds, tf.nn.softmax(output, axis = 1).numpy()), axis = 0)

    # print(input)
    return { "ans": preds.tolist() }

    # text=request.get_json()['text']
    # return(predict(text, finbert.model).to_json(orient='records'))

@app.route("/tweetbert",methods=['POST'])
def score_tweet():
    logger.info("Beginning to load TweetBERT model")
    tweetbert = TweetBERT()
    texts=request.get_json()['texts']
    preds = np.array([]).reshape((0, 3))
    num_chunks = (len(texts) + 1)//size
    for i, batch in enumerate(chunk(texts, size)):
        logger.info(f"Processed chunk {i} out of {num_chunks}")
        input = tweetbert.tokenizer(batch, return_tensors="tf", padding = True)
        # print(input)
        output = tweetbert.model(input).logits
        preds = np.concatenate((preds, tf.nn.softmax(output, axis = 1).numpy()[:, [2, 0, 1]]), axis = 0)

    # print(input)
    return { "ans": preds.tolist() }

@app.route("/news-classification",methods=['POST'])
def classify_news():
    logger.info("Beginning to load news classification model")
    news_classification = NewsClassification()
    texts=request.get_json()['texts']
    preds = []
    num_chunks = (len(texts) + 1)//size
    for i, batch in enumerate(chunk(texts, size)):
        logger.info(f"Processed chunk {i} out of {num_chunks}")
        input = news_classification.tokenizer(batch, return_tensors="pt", padding = True)["input_ids"]
        # print(input)
        output = news_classification.model(input).logits.cpu().detach()
        vecs = tf.nn.softmax(output, axis = 1).numpy().reshape((-1, 4)).tolist()
        logging.info(type(news_classification.id2label[0]))
        #logging.info({news_classification.id2label[label]: vec[label] for label in range(0, 4)})
        for j, text in enumerate(batch):
            preds.append({
                "text": text,
                "vec": vecs[j],
                "classes": {value: float(vecs[j][key]) for key, value in news_classification.id2label.items()}
            })

    # print(input)
    return jsonify({ "ans": preds })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)