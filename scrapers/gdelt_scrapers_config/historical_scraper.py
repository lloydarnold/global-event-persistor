from google.cloud import bigquery
from google.oauth2 import service_account
import scutility
import requests
import configparser
import json
import classification

config = configparser.RawConfigParser()
config.read(filenames = './historical_config')

db_endpoint = config.get('database', 'DB_ENDPOINT')
is_fips = int(config.get('database', 'IS_FIPS'))
entries_cap = int(config.get('database', 'ENTRIES_CAP'))
category_classify = json.loads(config.get('database', 'CATEGORY_CLASSIFY').lower())
news_classify = json.loads(config.get('database', 'NEWS_CLASSIFY').lower())

account_file = config.get('google', 'ACCOUNT_FILE')
google_scopes = json.loads(config.get('google', 'GOOGLE_SCOPES'))

query_file = config.get('query', 'QUERY_FILE')

# Converts raw gdelt entries to python dictionary with our own fields
def convert(entry):
    date = str(entry.SQLDATE)
    
    # regions only store countries for now
    # TODO: make regions store city/state as well.
    regions = []
    if entry.Actor1Geo_CountryCode:
        regions.append({
            "isFIPS": is_fips,
            "country": entry.Actor1Geo_CountryCode
        })
        # regions.append(["continent", entry.Actor1Geo_CountryCode, entry.Actor1Geo_ADM1Code, "city"])
    if entry.Actor2Geo_CountryCode:
        regions.append({
            "isFIPS": is_fips,
            "country": entry.Actor2Geo_CountryCode
        })
        # regions.append(["continent", entry.Actor2Geo_CountryCode, entry.Actor2Geo_ADM1Code, "city"])
    if entry.ActionGeo_CountryCode:
        regions.append({
            "isFIPS": is_fips,
            "country": entry.ActionGeo_CountryCode
        })
        # regions.append(["continent", entry.ActionGeo_CountryCode, entry.ActionGeo_ADM1Code, "city"])
    
    return {
        "timeStamp": date[:4]+"-"+date[4:6]+"-"+date[6:8],
        "positivity": entry.AvgTone,
        "relevance": entry.GoldsteinScale,
        "source": entry.SOURCEURL,
        "category": "",
        "subcategory": "", # TODO: Implement subcategories
        "detail": entry.SOURCEURL,
        "actors": [entry.Actor1Name, entry.Actor2Name],
        "stocks": [], # TODO: Get used stocks
        "eventRegions": regions
    }


def main():
    # Credential file for bigquery
    credentials = service_account.Credentials.from_service_account_file(
        account_file, scopes=google_scopes
    )

    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    file = open(query_file, "r")
    lines = file.readlines()
    query=""
    for line in lines:
        query += line
    print(query)

    # Sends query to bigquery
    query_job = client.query(query, job_config=bigquery.QueryJobConfig())
    data = query_job.result()
    rows = list(data)

    #entries will store the data points that will be used to create the dictionaries for each event
    entries = []

    for i, row in enumerate(rows):
        if entries_cap != -1 and i >= entries_cap:
            break
        entries.append(convert(row))
        print(convert(row))

    #final_list stores the dictionaries of each event which will be the json data to send as a body
    final_list = []

    for entry in entries:
        final_list.append(entry)

    if category_classify:
        scutility.classify_entries(final_list)

        #Fake news classification
    if news_classify:
        predictions = classification.news_classification(final_list)
        temp = ["unlikely","likely"]
        for i in range(0, len(final_list)):
            if predictions[i]!=-1:
                final_list[i]['detail'] += ", this "+temp[predictions[i]]+ " to be fake news"


    r = requests.post(db_endpoint, json=final_list)

    print(f"Status Code: {r.status_code}, Response: {r.json()}")


if __name__ == "__main__":
    main()
