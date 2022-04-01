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

    region=entry.Actor1CountryCode

    actors=[entry.Actor1Name, entry.Actor2Name]

    stocks=[]
    
    return [timeStamp, positivity, relevance, source, category, subcategory, detail, region, actors, stocks]

credentials = service_account.Credentials.from_service_account_file(
    'service-account-file.json', scopes=['https://www.googleapis.com/auth/cloud-platform']
)

client = bigquery.Client(credentials=credentials, project=credentials.project_id)

file = open("query.txt", "r") 
lines = file.readlines()

#Converting file into query:
string=""
for i in lines:
    string += i

print(string)

query = string

#The query:
query_job = client.query(query, job_config=bigquery.QueryJobConfig())
data = query_job.result()
rows = list(data)

#Convert the first (and only asuming LIMIT 1 is used in the query) element returned by the query so that we can add it to the DB
entryList=convert(rows[0])

#Send the add request
r = requests.post('http://localhost:3000/events', json=  {
    "timeStamp": entryList[0],
    "positivity": entryList[1],
    "relevance": entryList[2],
    "source": entryList[3],
    "category": entryList[4],
    "subcategory": entryList[5],
    "detail": entryList[6],
    "region": entryList[7],
    "actors": entryList[8],
    "stocks": entryList[9]
    })

print(f"Status Code: {r.status_code}, Response: {r.json()}")

