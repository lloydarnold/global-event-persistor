import requests
import lxml.html as lh
import os.path
import zipfile
import scutility
from newsplease import NewsPlease

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

def filterEntry(entry,input_lines):

    lines = []
    for i in input_lines:
        lines.append(i)

    boolean = True
    
    #Date filter:
    if len(lines[0][0])!=0:
        boolean = compareDates(lines[0][0],entry["timeStamp"]) and compareDates(entry["timeStamp"],lines[0][1]) 

    #Positivity filter:
    if len(lines[1][0])!=0:
        boolean = boolean and int(lines[1][0])<=entry["positivity"] and int(lines[1][1])>=entry["positivity"]

    #Relevance filter:
    if len(lines[2][0])!=0:
        boolean = boolean and int(lines[2][0])<=entry["relevance"] and int(lines[2][1])>=entry["relevance"]

    #Source filter:

    #category filter:

    #subcategory filter:

    #detail filter:

    #actors filter:
    if len(lines[7][0][0])!=0:

        for i in lines[7]:
            tempBool=False
            for x in i:
                if x in entry["actors"]:
                    tempBool=True
            boolean = boolean and tempBool

    #stocks filter:

    #eventRegions filter:
    if len(lines[9][0][0])!=0:

        for i in lines[9]:
            tempBool=False
            for x in i:
                if {"country":x} in entry["eventRegions"]:
                    tempBool=True
            boolean = boolean and tempBool

    return boolean 

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
            "country": entry[fields.index("Actor1Geo_CountryCode")]
        })
    if entry[fields.index("Actor2Geo_CountryCode")]:
        regions.append({
            "country": entry[fields.index("Actor2Geo_CountryCode")]
        })
    if entry[fields.index("ActionGeo_CountryCode")]:
        regions.append({
            "country": entry[fields.index("ActionGeo_CountryCode")]
        })
    
    # Classify stuff
    # category = ""
    # url = "http://127.0.0.1:8080/news-classification"
    # try:
    #     source_url = entry[fields.index("SOURCEURL")]
    #     news = NewsPlease.from_url(source_url).get_dict()
    #     js = {"texts": [news["title"]]}
    #     res = requests.post(url, json=js)
    #     category = res.json()["ans"]
    # except:
    #     category = "ERROR" # This will be used to filter stuff below, won't make it to our database
    
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
    gdelt_base_url = "http://data.gdeltproject.org/events/"

    file = open("filter.txt","r") #filter the entries:
    lines = file.readlines()
    file.close()

    while len(lines)<10:
        lines.append("")

    for i in range(0,len(lines)):
        lines[i]=lines[i].strip("\n").split(",")

    for i in range(0, len(lines[7])):
        lines[7][i] = lines[7][i].split("/")

    for i in range(0, len(lines[9])):
        lines[9][i] = lines[9][i].split("/")

    # get the list of all the links on the gdelt file page
    page = requests.get(gdelt_base_url+'index.html')
    doc = lh.fromstring(page.content)
    link_list = doc.xpath("//*/ul/li/a/@href")

    # separate out those links that begin with four digits, then get the most recent entry (with index 0) 
    zip_file = [x for x in link_list if str.isdigit(x[0:4])][0]
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
                converted_entries.append(converted_entry)
                # if converted_entry["category"] != "ERROR":
                #     data.append(converted_entry)
                #     r = requests.post("http://localhost:3000/events", json=converted_entry)
                #     if r.status_code != 201:
                #         print(f"Status Code: {r.status_code}, Response: {r.json()}")
                #     else:
                #         print(f"Status Code: {r.status_code}, Success")
            except:
                print("An exception occured when parsing this entry")
    
    converted_entries = converted_entries[:10] # limitting to 10 entries for testing
    
    print("classifying...")
    scutility.classify_entries(converted_entries)

    print("uploading...")
    for converted_entry in converted_entries:
        if filterEntry(converted_entry,lines):
            if converted_entry["category"] != "INVALID_SOURCE":
                r = requests.post("http://localhost:3000/events", json=converted_entry)
                if r.status_code != 201:
                    print(f"Status Code: {r.status_code}, Response: {r.json()}")
                else:
                    print(f"Status Code: {r.status_code}, Success")
            else:
                print("INVALID_SOURCE")
    
    # delete .csv file
    os.remove(csv_file)
    
    print("done!")


def get_category(texts, url = 'http://127.0.0.1:8080/news-classification'):
    js = { 'texts': texts }
    res = requests.post(url, json = js)
    return res.json()['ans']

if __name__ == "__main__":
    main()