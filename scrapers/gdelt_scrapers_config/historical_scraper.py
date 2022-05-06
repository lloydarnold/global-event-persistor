from google.cloud import bigquery
from google.oauth2 import service_account
import scutility
import requests
import configparser
import json
import classification

config = configparser.RawConfigParser()
config.read(filenames = './historical_config')

try:
    db_endpoint = config.get('database', 'DB_ENDPOINT')
    global_is_fips = int(config.get('database', 'GLOBAL_IS_FIPS'))
    america_is_fips = int(config.get('database', 'AMERICA_IS_FIPS'))
    entries_cap = int(config.get('database', 'ENTRIES_CAP'))
    category_classify = json.loads(config.get('database', 'CATEGORY_CLASSIFY').lower())
    news_classify = json.loads(config.get('database', 'NEWS_CLASSIFY').lower())

    account_file = config.get('google', 'ACCOUNT_FILE')
    google_scopes = json.loads(config.get('google', 'GOOGLE_SCOPES'))

    query_file = config.get('query', 'QUERY_FILE')
except:
    print("Check config file")
    exit()
    
# Converts raw gdelt entries to python dictionary with our own fields
def convert(entry):
    date = str(entry.SQLDATE)
    
    regions=[]
    if(entry.ActionGeo_Type != 0):
        regions.append(createRegion(entry.ActionGeo_Type, entry.ActionGeo_CountryCode, entry.ActionGeo_ADM1Code, entry.ActionGeo_FullName))
    if(entry.Actor1Geo_Type != 0 and entry.Actor1Geo_FullName != entry.ActionGeo_FullName):
        regions.append(createRegion(entry.Actor1Geo_Type, entry.Actor1Geo_CountryCode, entry.Actor1Geo_ADM1Code, entry.Actor1Geo_FullName))
    if(entry.Actor2Geo_Type != 0 and entry.Actor2Geo_FullName != entry.ActionGeo_FullName and entry.Actor2Geo_FullName != entry.Actor1Geo_FullName):
        regions.append(createRegion(entry.Actor2Geo_Type, entry.Actor2Geo_CountryCode, entry.Actor2Geo_ADM1Code, entry.Actor2Geo_FullName))
    
    actors=[]
    if(entry.Actor1Name != None):
        actors.append(entry.Actor1Name)
    if(entry.Actor2Name != None and entry.Actor2Name != entry.Actor1Name):
        actors.append(entry.Actor2Name)
    
    return {
        "timeStamp": date[:4]+"-"+date[4:6]+"-"+date[6:8],
        "positivity": entry.AvgTone,
        "relevance": entry.GoldsteinScale,
        "source": entry.SOURCEURL,
        "category": "",
        "subcategory": "", # TODO: Implement subcategories
        "detail": entry.SOURCEURL,
        "actors": actors,
        "stocks": [], # TODO: Get used stocks
        "eventRegions": regions
    }

def createRegion(type, countryCode, ADM1Code, fullname):
    if(type == 1): #Country
        return {"isFIPS": global_is_fips, "country": countryCode}
    if(type == 2): #US State
        return {"isFIPS": america_is_fips, "country": countryCode, "state": getUsState(ADM1Code)}
    if(type == 5): #World State
        return {"isFIPS": global_is_fips, "country": countryCode, "state": ADM1Code}
    if(type == 3): #US City
        if(ADM1Code != countryCode):
            return {"isFIPS": america_is_fips, "country": countryCode, "state": getUsState(ADM1Code), "city":getCity(fullname)}
        else: #State not given
            return {"isFIPS": america_is_fips, "country": countryCode, "city": getCity(fullname)}
    if(type == 4): #World City
        if(ADM1Code != countryCode):
            return {"isFIPS": global_is_fips, "country": countryCode, "state": ADM1Code, "city":getCity(fullname)}
        else: #State not given
            return {"isFIPS": global_is_fips, "country": countryCode, "city": getCity(fullname)}

def getCity(fullname):
    c = fullname.find(',')
    return fullname[0:c]

def getUsState(ADM1Code):
    return ADM1Code[:2] + '-' + ADM1Code[2:]

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
    try:
        query_job = client.query(query, job_config=bigquery.QueryJobConfig())
    except:
        print("Check query")
        exit()
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

    if category_classify and len(final_list)!=0:
        scutility.classify_entries(final_list)

        #Fake news classification
    if news_classify and len(final_list)!=0:
        predictions = classification.news_classification(final_list)
        temp = ["unlikely","likely"]
        for i in range(0, len(final_list)):
            if final_list[i]["category"] == "INVALID_SOURCE" or final_list[i]["category"]=="":
                final_list[i]["category"] = "NA"
            if predictions[i]!=-1:
                final_list[i]['detail'] += ", this is "+temp[predictions[i]]+ " to be fake news"

    if len(final_list)!=0:
        r = requests.post(db_endpoint, json=final_list)

        print(f"Status Code: {r.status_code}, Response: {r.json()}")
        
    else:
        print("No entries found")


if __name__ == "__main__":
    main()
