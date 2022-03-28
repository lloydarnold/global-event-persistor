## Backtesting Framework

### Database Schema
#### High Level Explanation
We will be using two mongo collections to store information; one that stores
  events and one that stores locations. The location database will be populated
  with entries storing hierarchical location data; the events database will
  store location of event by storing the ID of an object in this database. Thus,
  the relationship between events and locations is many to one.

This is advantageous in two obvious ways. One - it makes searching by geographical
  region slightly efficient, as searches are done by querying the location DB and
  then searching with this ID. Two - it allows testers to easily check which
  locations are covered, and can be used to provide validation / auto-prediction
  of location before querying (potentially large) events DB.

#### Events Schema
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
  continent / country / province codes, city full names

    continent : String,
    country : String,
    state: String,
    city : String

### Queries
We are creating a REST API for events. The address of this will obviously be
  set when we deploy and find hosting. All queries are currently responded to via
  sending a JSON over a socket, containing matching events stored as in the
  above schema, if request is valid and such events exist. At present, there is
  no authentication - we will review how best to introduce this, but is likely
  to involve having a security key as a parameter on all requests. Could
  potentially also do it by network if this was for some reason easier.

If a parameter isn't given, the code will send a warning, but default to `ALL`

Provisionally, it will accept the following operations. This can be expanded if
  required :

    get-all - returns all events
      possible error codes : Permission-Denied
      Example use :
        <host>:<port>/events/get-all

    get-in-range - returns events between two dates.
      Params :- from:Date, to:Date
      possible errors : Permission-Denied, From-Date-Invalid, To-Date-Invalid
      Example use :
        <host>:<port>/events/get-in-range?from=01 Jan 1970 00:00:00 GMT&
          to=11 Jan 1970 00:00:00 GMT

    get-regions - returns all regions
      possible error codes : Permission-Denied
      Example use :
        <host>:<port>/events/get-regions

    get-by-region - returns events by a given locality
      Params :- continent:String, county:String, state: String, city: String
      possible errors : Permission-Denied, Invalid-Continent, Invalid-Country,
        Invalid-State, City-Not-Found
      Example Use :
        <host>:<port>/events/get-by-region?continent=OC&country=AUS
          &state=QUEENSLAND&city=ALL

    get-stock - query for events relating to particular stock / commodity / crypto
      Params :- stock:String
      possible errors : Permission-Denied, Stock-Not-Tracked
      Example Use :
        <host>:<port>/events/get-stock?stock=AAPL

    get-category - query for events in particular category / subcategory
      Params :- category:String, subcategory:String
      possible errors : Permission-Denied, Cat-Not-Found, Sub-Cat-Not-Found
      Example Use :
        <host>:<port>/events/get-category?category=EXW&subcategory=TOR

    get-events - query by all criteria above at once
      Params :- from:Date, to:Date, continent:String, county:String, 
                state: String, city: String, stock:String, category:String, subcategory:String
      possible errors : Permission-Denied, From-Date-Invalid, To-Date-Invalid,  Invalid-Continent, 
                        Invalid-Country,Invalid-State, City-Not-Found,  Stock-Not-Tracked, 
                        Cat-Not-Found, Sub-Cat-Not-Found
      Example Use:
        <host>:<port>/events/get-events?from=2022-02-03&to=2022-03-03&continent=NA&country=USA
          &state=CALIFORNIA&city=CUPERTINO&stock=AAPL&category=EXW&subcategory=TOR
