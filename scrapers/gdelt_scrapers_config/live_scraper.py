import requests
import lxml.html as lh
import os.path
import zipfile
import scutility
from newsplease import NewsPlease
import configparser
import json

config = configparser.RawConfigParser()
config.read(filenames = './live_config')

db_endpoint = config.get('database', 'DB_ENDPOINT')
is_fips = int(config.get('database', 'IS_FIPS'))
entries_cap = int(config.get('database','ENTRIES_CAP'))

date_range = json.loads(config.get('filter', 'DATE_RANGE'))
pos_range = json.loads(config.get('filter', 'POS_RANGE'))
rel_range = json.loads(config.get('filter', 'REL_RANGE'))
category_list = json.loads(config.get('filter', 'CATEGORY_LIST'))
actor_list = json.loads(config.get('filter', 'ACTOR_LIST'))
country_list = json.loads(config.get('filter', 'COUNTRY_LIST'))

gdelt_base_url = config.get('gdelt', 'GDELT_URL')
gdelt_file = int(config.get('gdelt', 'GDELT_FILE'))

fields = [
    "GLOBALEVENTID",
    "SQLDATE",
    "MonthYear",
    "Year",
    "FractionDate",
    "Actor1Code",
    "Actor1Name",
    "Actor1CountryCode",
    "Actor1KnownGroupCode",
    "Actor1EthnicCode",
    "Actor1Religion1Code",
    "Actor1Religion2Code",
    "Actor1Type1Code",
    "Actor1Type2Code",
    "Actor1Type3Code",
    "Actor2Code",
    "Actor2Name",
    "Actor2CountryCode",
    "Actor2KnownGroupCode",
    "Actor2EthnicCode",
    "Actor2Religion1Code",
    "Actor2Religion2Code",
    "Actor2Type1Code",
    "Actor2Type2Code",
    "Actor2Type3Code",
    "IsRootEvent",
    "EventCode",
    "EventBaseCode",
    "EventRootCode",
    "QuadClass",
    "GoldsteinScale",
    "NumMentions",
    "NumSources",
    "NumArticles",
    "AvgTone",
    "Actor1Geo_Type",
    "Actor1Geo_FullName",
    "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code",
    "Actor1Geo_Lat",
    "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type",
    "Actor2Geo_FullName",
    "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code",
    "Actor2Geo_Lat",
    "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type",
    "ActionGeo_FullName",
    "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code",
    "ActionGeo_Lat",
    "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED",
    "SOURCEURL"
]

def filterEntry(entry):

    boolean = True
    
    #Date filter:
    if len(date_range)!=0:
        boolean = compareDates(date_range[0],entry["timeStamp"]) and compareDates(entry["timeStamp"],date_range[1]) 

    #Positivity filter:
    if len(pos_range)!=0:
        boolean = boolean and int(pos_range[0])<=entry["positivity"] and int(pos_range[1])>=entry["positivity"]

    #Relevance filter:
    if len(rel_range)!=0:
        boolean = boolean and int(rel_range[0])<=entry["relevance"] and int(rel_range[1])>=entry["relevance"]

    #Source filter:

    #category filter:

    #subcategory filter:

    #detail filter:

    #actors filter:
    if len(actor_list)!=0:

        for i in actor_list:
            tempBool=False
            for x in i:
                if x in entry["actors"]:
                    tempBool=True
            boolean = boolean and tempBool

    #stocks filter:

    #eventRegions filter:
    if len(country_list)!=0:

        for i in country_list:
            tempBool=False
            for x in i:
                if {"country":x} in entry["eventRegions"] or {"isFIPS": 1, "country":x} in entry["eventRegions"]:
                    tempBool=True
            boolean = boolean and tempBool

    return boolean 

def categoryFilter(entry):
    if len(category_list)!=0:
        if entry["category"] not in category_list:
            return False
    return True

def compareDates(date1, date2): #Returns true if date1<=date2
    if int(date1[:4]) > int(date2[:4]):
        return False
    elif int(date1[:4]) < int(date2[:4]):
        return True
    else:
        if int(date1[5:7]) > int(date2[5:7]):
            return False
        elif int(date1[5:7]) < int(date2[5:7]):
            return True
        else:
            if int(date1[8:10]) > int(date2[8:10]):
                return False
            elif int(date1[8:10]) < int(date2[8:10]):
                return True
            else:
                return True

def convert(entry):
    date = entry[fields.index("SQLDATE")]
    
    # regions only store countries for now
    # TODO: make regions store city/state as well.
    regions = []
    if entry[fields.index("Actor1Geo_CountryCode")]:
        regions.append({
            "isFIPS": is_fips,
            "country": entry[fields.index("Actor1Geo_CountryCode")]
        })
    if entry[fields.index("Actor2Geo_CountryCode")]:
        regions.append({
            "isFIPS": is_fips,
            "country": entry[fields.index("Actor2Geo_CountryCode")]
        })
    if entry[fields.index("ActionGeo_CountryCode")]:
        regions.append({
            "isFIPS": is_fips,
            "country": entry[fields.index("ActionGeo_CountryCode")]
        })
    
    return {
        "timeStamp": date[:4]+"-"+date[4:6]+"-"+date[6:8],
        "positivity": float(entry[fields.index("AvgTone")]),
        "relevance": float(entry[fields.index("GoldsteinScale")]),
        "source": entry[fields.index("SOURCEURL")],
        "category": "",
        "subcategory": "", # TODO: Implement subcategories
        "detail": entry[fields.index("SOURCEURL")],
        "actors": [entry[fields.index("Actor1Name")], entry[fields.index("Actor2Name")]],
        "stocks": [], # TODO: Get used stocks
        "eventRegions": regions
    }


def main():
    # Date validation
    if len(date_range)!=0:
        if len(date_range)!=2 or len(date_range[0])!=10 or len(date_range[1])!=10 or date_range[0][4]!="-" or date_range[1][4]!="-" or date_range[0][7]!="-" or date_range[1][7]!="-":
            print("Fix the dates in the filter")
            exit()
        else:
            try:
                int(date_range[0][:4])
                int(date_range[1][:4])
                int(date_range[0][5:7])
                int(date_range[1][5:7])
                int(date_range[0][8:])
                int(date_range[1][8:])
            except:
                print("Fix the dates in the filter")
                exit()

    # Positivity validation

    if len(pos_range)!=0:
        if len(pos_range)!=2:
            print("Fix the positivity range in the filter")
            exit()
        else:
            try:
                int(pos_range[0])
                int(pos_range[1])
            except:
                print("Fix the positivity range in the filter")
                exit()

    # Relativity validation

    if len(rel_range)!=0:
        if  len(rel_range)!=2:

            print("Fix the relativity range in the filter")
            exit()
        else:
            try:
                int(rel_range[0])
                int(rel_range[1])
            except:
                print("Fix the relativity range in the filter")
                exit()

    # get the list of all the links on the gdelt file page
    page = requests.get(gdelt_base_url+'index.html')
    doc = lh.fromstring(page.content)
    link_list = doc.xpath("//*/ul/li/a/@href")

    # separate out those links that begin with four digits, then get the most recent entry (with index 0) 
    zip_file = [x for x in link_list if str.isdigit(x[0:4])][gdelt_file]
    print(zip_file)

    # if we dont have the compressed file stored locally, go get it. Keep trying if necessary.
    while not os.path.isfile(zip_file): 
        print("downloading...")
        with requests.get(url=gdelt_base_url+zip_file, stream=True) as r:
            r.raise_for_status()
            with open(zip_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

    # extract the contents of the compressed file    
    print("extracting...")
    with zipfile.ZipFile(file=zip_file, mode="r") as z:
        z.extractall(path="")

    # delete the downloaded zip file
    os.remove(zip_file)

    csv_file = zip_file[:-4]
    print(csv_file)

    print("parsing...")
    converted_entries = []
    with open(csv_file, mode="r", encoding="utf-8") as entries:
        for entry in entries:
            try:
                converted_entry = convert(entry.split("\t"))
                if filterEntry(converted_entry):
                    converted_entries.append(converted_entry)
            except:
                print("An exception occured when parsing this entry")
    
    converted_entries = converted_entries[:entries_cap] # limitting to 10 entries for testing
    
    print("classifying...")
    scutility.classify_entries(converted_entries)

    print("uploading...")
    final_entries = []
    for converted_entry in converted_entries:
        if categoryFilter(converted_entry):
            if converted_entry["category"] == "INVALID_SOURCE":
                converted_entry["category"] == ""
            final_entries.append(converted_entry)

    r = requests.post(db_endpoint, json=final_entries)
    print(f"Status Code: {r.status_code}")
    
    # delete .csv file
    os.remove(csv_file)
    
    print("done!")

if __name__ == "__main__":
    main()