# Inference API for sentiment analysis and text classification

## Setup

On the initial run, the conda environment must be created (this can take a while):
```
cd scrapers/language_models
conda env create -f environment.yml
```

After that, you can start the API as follows:
```
cd scrapers/language_models
source setup.bash
flask run --port 8080
```

## Endpoints

All 3 models in this API are obtained from https://huggingface.co/ via its `transformers` library. The API runs on Flask. For memory reasons, each model is loaded into memory each time a request comes in for it, so that not all 3 need to be in memory at once.

FinBERT: <base_url>/finbert
TweetBERT: <base_url>/tweetbert
News Classification: <base_url>/news-classification

### Requests

The endpoints accept post requests with a JSON of the format:

```
{
    "texts": <array containing the texts to be fed to the model>
}
```

The sentiment analysis APIs return a JSON of the format:
```
{
    "ans": <array containing sentiment vectors for each text>
}
```

The i'th sentiment vector corresponds to the i'th text sent to the model. A sentiment vector is a tuple [p_positive, p_negative, p_neutral], with 3 positive entries that add up to 1 and represent the confidence of the model that each of the 3 sentiments is present in the given text.

The news classification endpoint outputs the following format:
```
{
    "ans": [
        {
            "text": text_1,
            "vec": probability distribution over classes,
            "classes": name of each class corresponding to each entry in the probability distribution
        }, 
        .
        .
        .

        {
            "text": text_n,
            "vec": probability distribution over classes for text_n,
            "classes": name of each class corresponding to each entry in the probability distribution
        },
    ]
}
```