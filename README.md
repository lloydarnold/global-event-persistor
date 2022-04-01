# global-event-persistor
A Group Practical Project for CS course at Oxford, developed in conjunction with ApexE3. A global event data persistor, that scrapes political, financial and cultural events amongst others and stores them in a database.

## Backend Framework

### Database Schema

There are two database tables in use in our project; one that stores event data
  and one that stores locations. The location database will be populated
  with entries storing hierarchical location data; the events database will
  store location of event by storing the ID of an object in this database. Thus,
  the relationship between events and locations is many to one.

Location data is encoded using standard ISO Alpha-2 codes - these can be found
  in .json files in `./backend/src/res`. The program validates to ensure that
  entries are of the correct form, and that countries are in continents /
  states in countries. There is no validation on cities as this was deemed
  intractable, but city names are capitalized and stripped of accents.

  Our events database will store the following datapoints /types.

      timeStamp: Date,
      sentiment: {positivity: Number, goldstein: Number}
        (positivity, provided by GDELT, between -100 and 100. For
        non GDELT sources we will explore using NLP to generate a similar score.
        Goldstein is a proxy for importance.),
      source: String,
      category: String - from finite list, verified at controller level. See below
        for initial idea of categories. Stored in external file, so easy to update
        later,
      subcategory: String - see note re category,
      detail : String,
      region : ObjectID from location DB - see above,
      actors : [String],
      stocks : [String]

##### Categories
  Taken from specification provided by Apex. Every category / subcategory has an
    event code.

      Financial (FIN) :
        - Company earnings reports (CER)
        - Product Launches (PRL)
        - Org Changes (OCH)
        - Lawsuits (LAW)
        - M&A (mergers & acquisitions) (MA)
      Macro Economic (MEC) :
        - Employment data (EMPD)
        - Key Economic Indicators (KEI)
        - Interest Rates (INR)
        - QE (quantitative easing) (QE)
      Geopolitical (GEOP) :
        - Trade wars (TRW)
        - Elections (ELEC)
        - Referendums (REF)
        - Flash Points (FLP)
        - Coups (COU)
        - Changes in Government (CIG)
        - Trade Deals (TRD)
      Extreme weather events (EXW) :
        - Hurricanes hitting landfall (HUR)
        - Named Storms (NST)
        - Earthquakes (EQ)
        - Tsunami’s (TSU)
        - Tornadoes (TOR)
      Sports events (SPO) :
        - Football (FOOT)
        - American Football (AMFOOT)
        - Cricket (CRI)
        - Baseball (BASE)
        - Formula 1 (FONE)
        - Golf (GOLF)
        - Rugby (RUG)
        - Olympic (OLY)
      Entertainment events (ENT) :
        - Music launch (MUS)
        - Movie release (MOV)
        - Game Launch (GAME)
        - Stadium Events (STD)
      Misc events (MISC) :
        - Trainer/Clothing launch (FAL)

#### Location Schema
  A very simple database, just stores location in hierarchical manner. Uses ISO
    continent / country / province codes, city full names accent free.

      continent : String,
      country : String,
      state: String,
      city : String

### API Endpoints and Usage

We are creating a REST API for events. The address of this will obviously be
  set when we deploy and find hosting. All queries are currently responded to via
  sending a JSON over a socket, containing matching events stored as in the
  above schema, if request is valid and such events exist. At present, there is
  no authentication - we will review how best to introduce this, but is likely
  to involve having a security key as a parameter on all requests. Could
  potentially also do it by network if this was for some reason easier.

  If a parameter isn't given, the program will send a warning, but default to `ALL` - this may be reviewed at a later date.

  The following operations and usages are defined :


##### create event
  creates a single new event. Default behavior on
    receiving a post request. Contents should be in body of request, as a
    JSON. All database categories that are desired should be filled out.

  Requests should be directed to :
    `<host>:<port:/events`

  Example body of request :

```
  {
    "timeStamp" : "Tue 29 Mar 2022 02:56:15" ,
    "source" : "example",
    "relevance" : -4,
    "positivity" : 17,
    "category" : "GEOP",
    "subcategory" : "REF",
    "detail": "example referendum regarding code efficacy in munich",
    "continent":"Europe",
    "country": "GE",
    "state" : "Bavaria",
    "city" : "Munich",
    "actors" : ["lloyd"]
  }
```

##### create-many

 creates 1 or more events, preferred to standard create event

  POST requests directed to
    `<host>:<port:/events/create-many`

Body should be an array of objects as above, eg. body :
  ```

  [
      {
          "timeStamp": "2022-04-16",
          "sentiment": 100,
          "relevance": 1,
          "source": "Newspaper X",
          "category": "FIN",
          "subcategory": "PRL",
          "detail": "Tech companies made less money",
          "actors": ["Apple Inc.", "Tesla Inc."],
          "stocks": ["AAPL", "TSLA"],
          "city": "New York",
          "state": "New York",
          "country": "United States",
          "continent": "North America"
      },
      {
          "timeStamp": "2022-05-16",
          "sentiment": 100,
          "relevance": 5,
          "source": "Newspaper X",
          "category": "FIN",
          "subcategory": "PRL",
          "detail": "Tech companies made money this time",
          "actors": ["Apple Inc.", "Tesla Inc."],
          "stocks": ["AAPL", "TSLA"],
          "city": "São Paulo",
          "state": "São Paulo",
          "country": "Brazil",
          "continent": ""
      }
  ]
```

##### get-all
Returns all events.

possible error codes : `Permission Denied`

Example use :
    ``<host>:<port>/events/get-all``

##### get-in-range
Returns events between two timestamps, inclusive.

Possible error codes: `Permission-Denied, "message": "Cast to date
  failed for value \"NaN\" (type number) at path \"timeStamp\" for model
  \"Event\""`

Example use :
    `<host>:<port>/events/get-in-range?from=01 Jan 1970 00:00:00 GMT&
      to=11 Jan 1970 00:00:00 GMT`

##### get-regions
Returns all regions

possible error codes : `Permission-Denied`

Example use :
  `<host>:<port>/events/get-regions`

##### get-by-stock

Query for events relating to particular stock(s) / commodity(ies) / crypto(s)

Params : `stock:String[]`

possible errors : ` Permission-Denied `

Example Use :
    `<host>:<port>/events/get-by-stock?stocks[0]=AAPL&stocks[1]=TSLA`

##### get-by-category
Query for events in any of a list of categories/subcategories.

Params: `categories: string[], subcategories: string[]`

possible errors : `Permission denied, Invalid Category`

Example Use :
  ``<host>:<port>/events/get-by-category?category[0]=EXW&subcategory[0=TOR&category[1]=GEOP``

##### get-events

A generalized query. Use any combination of the above parameters.
