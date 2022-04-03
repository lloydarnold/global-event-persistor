from google.cloud import bigquery
from google.oauth2 import service_account
import requests


def convert(entry):
    date=str(entry.SQLDATE)
    timeStamp = date[:4]+"-"+date[4:6]+"-"+date[6:8]

    positivity=entry.AvgTone

    relevance=entry.GoldsteinScale

    source=entry.SOURCEURL

    category=entry.EventCode

    subcategory=""

    detail=entry.SOURCEURL

    region=["continent", entry.ActionGeo_CountryCode, entry.ActionGeo_ADM1Code, "city"]

    actors=[entry.Actor1Name, entry.Actor2Name]

    stocks=[]
    
    return [timeStamp, positivity, relevance, source, category, subcategory, detail, region, actors, stocks]

credentials = service_account.Credentials.from_service_account_file(
    'service-account-file.json', scopes=['https://www.googleapis.com/auth/cloud-platform']
)

client = bigquery.Client(credentials=credentials, project=credentials.project_id)

file = open("query.txt", "r")
lines = file.readlines()

#string will store the query

string=""
for i in lines:
    string += i

print(string)

# This is just a dummy query looking for things that are relevant to the uk
query = string

query_job = client.query(query, job_config=bigquery.QueryJobConfig())
data = query_job.result()
rows = list(data)

#fields = ["timeStamp", "positivity", "relevance", "source", "category", "subcategory", "detail", "region", "actors", "stocks"]

#entryList will store the data points that will be used to create the dictionaries for each event
entryList = []

for i in range(0, len(rows)):
    entryList.append(convert(rows[i]))

#finalList stores the dictionaries of each event which will be the json data to send as a body
finalList = []

for i in entryList:
    print(i)
    finalList.append({
    "timeStamp" : i[0],
    "positivity" : i[1],
    "relevance" : i[2],
    "source": i[3], 
    "category": i[4], 
    "subcategory": i[5], 
    "detail": i[6],
    "continent": i[7][0],
    "country": i[7][1],
    "state" : i[7][2],
    "city" : i[7][3],
    "actors": i[8], 
    "stocks": i[9]
      })


r = requests.post('http://localhost:3000/events/create-many', json=  finalList)

print(f"Status Code: {r.status_code}, Response: {r.json()}")
