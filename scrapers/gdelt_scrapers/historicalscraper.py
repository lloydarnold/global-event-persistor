from google.cloud import bigquery
from google.oauth2 import service_account
import scutility
import requests


# Converts raw gdelt entries to python dictionary with our own fields
def convert(entry):
    date = str(entry.SQLDATE)
    
    # regions only store countries for now
    # TODO: make regions store city/state as well.
    regions = []
    if entry.Actor1Geo_CountryCode:
        regions.append({
            "country": entry.Actor1Geo_CountryCode
        })
        # regions.append(["continent", entry.Actor1Geo_CountryCode, entry.Actor1Geo_ADM1Code, "city"])
    if entry.Actor2Geo_CountryCode:
        regions.append({
            "country": entry.Actor2Geo_CountryCode
        })
        # regions.append(["continent", entry.Actor2Geo_CountryCode, entry.Actor2Geo_ADM1Code, "city"])
    if entry.ActionGeo_CountryCode:
        regions.append({
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
        "service-account-file.json", scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    client = bigquery.Client(credentials=credentials, project=credentials.project_id)

    file = open("query.txt", "r")
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

    limit = -1
    # limit = int(input("limit? (put -1 for no limit) "))

    for i, row in enumerate(rows):
        if limit != -1 and i >= limit:
            break
        entries.append(convert(row))
        print(convert(row))

    #finalList stores the dictionaries of each event which will be the json data to send as a body
    finalList = []

    for entry in entries:
        finalList.append(entry)

    scutility.classify_entries(finalList)

    r = requests.post("http://localhost:3000/events/create-many", json=finalList)

    print(f"Status Code: {r.status_code}, Response: {r.json()}")


if __name__ == "__main__":
    main()