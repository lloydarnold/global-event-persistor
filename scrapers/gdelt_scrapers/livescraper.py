import requests
import lxml.html as lh
import os.path
# import urllib
import zipfile
import glob
import operator

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
    
    return {
        "timeStamp": date[:4]+"-"+date[4:6]+"-"+date[6:8],
        "positivity": float(entry[fields.index("AvgTone")]),
        "relevance": float(entry[fields.index("GoldsteinScale")]),
        "source": entry[fields.index("SOURCEURL")],
        "category": entry[fields.index("EventCode")],
        "subcategory": "", # TODO: Implement subcategories
        "detail": entry[fields.index("SOURCEURL")],
        "actors": [entry[fields.index("Actor1Name")], entry[fields.index("Actor2Name")]],
        "stocks": [], # TODO: Get used stocks
        "eventRegions": regions
    }


def main():
    gdelt_base_url = "http://data.gdeltproject.org/events/"

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

    print("uploading...")
    data = []
    with open(csv_file, mode="r", encoding="utf-8") as entries:
        for entry in entries:
            try:
                converted_entry = convert(entry.split("\t"))
                if converted_entry["relevance"] > 9.0:
                    data.append(converted_entry)
                    r = requests.post("http://localhost:3000/events", json=converted_entry)
                    if r.status_code != 201:
                        print(f"Status Code: {r.status_code}, Response: {r.json()}")
                    else:
                        print(f"Status Code: {r.status_code}, Success")
            except:
                print("An exception occured when parsing this row")
    
    # delete .csv file
    os.remove(csv_file)
    
    print("done!")

    # r = requests.post("http://localhost:3000/events/create-many", json=data)

    # print(f"Status Code: {r.status_code}, Response: {r.json()}")


if __name__ == "__main__":
    main()