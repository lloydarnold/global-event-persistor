import requests
from tqdm import tqdm
from newsplease import NewsPlease
import configparser

config = configparser.RawConfigParser()
config.read(filenames = './scutility_config')

try:
    classification_url = config.get('inference', 'CLASSIFICATION_URL')
except:
    print("Check config file")
    exit()

def classify_entries(entries: list[dict]) -> None:
    """Classifies entries; Puts 'INVALID_SOURCE' if the source url is not a valid web page"""
    
    url = classification_url
    valid_titles = []
    
    for entry in tqdm(entries, desc="Getting Titles..."):
        try:
            source_url = entry["source"]
            n = NewsPlease.from_url(source_url)
            
            title = n.get_dict()["title"]
            valid_titles.append(title)
            # print(valid_titles[:10])
        except:
            entry["category"] = "INVALID_SOURCE"
    
    js = {"texts": valid_titles}
    res = requests.post(url, json=js)
    classifications = [max(d["classes"], key=d["classes"].get) for d in res.json()["ans"]]

    i = 0
    for entry in entries:
        if entry["category"] != "INVALID_SOURCE":
            entry["category"] = classifications[i]
            i += 1
    assert i == len(classifications)
