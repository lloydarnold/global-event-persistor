## Database Schema

### notes on relational vs. non-relational
- for this project, favor non-relational as flexibility is important - potential
  for future iterations to require changes to schema and or/expansion - relational
  databases require vertical scaling which is expensive and are not well suited
  to changes
- through careful code design, we can ensure that the backend processor could
  easily be switched to use a relational database in the future - specifically,
  ensure that all database related code is put into separate subroutines - insert,
  request etc etc

### Event categories ApexE3 are interested in
- Financial – Company earnings reports, product launches, org changes, lawsuits,
  M & A (mergers & acquisitions)
- Macro Economic – Employment data, key economic indicators, interest rates, QE
  (quantitative easing)
- Geopolitical – Trade wars, elections, referendums, flash points, coups,
  changes in government, (trade deals ?)
- Extreme weather events – Hurricanes hitting landfall, storms, earthquakes,
  tsunami’s, tornadoes
- Sports events – Football, American football, cricket, baseball, formula 1, golf, (rugby),
  (olympics)
- Entertainment events – Music launch, movie release, game launch, stadium events
- Misc events – Music launch, movie release, game launch, stadium events, trainer/clothing launch
    - this has heavy overlap with entertainment

#### Formalizing
This lends itself to categories and subcategories, with categories as above, subcategories
  as listed above. Shorten categories to codes, eg. FIN, MEC, GPL etc. but leave
  subcategories as is.

Do **not** hard code categories - include in separate file to allow for easy
  expansion in future.

### Other Categories
- event ID - needs to be unique.
  - One idea - hash timestamp with event name?
  - or - just timestamp to millisecond ? (in event of clash, just increment)
  - several other ways we could do this
  - alternatively, mongo *does* assign an id manually if we don't - could use
    this feature
- timestamp
  - time stamp of either event or (more likely) article
    - note re article -- need to be careful not to get rogue results from pieces
      such as event X ten years on - could split this and store article date and
      (estimated) date of event ?
    - mongo well suited to this - could put both under timestamp - timestamp.event
      / timestamp.source
- detail - event title, etc
- region - hierarchy - continent, region, country, region, county (?), city
  - for events that cover larger region, put ALL or similar in lower tiers
    - eg. european gas prices go up -> continent EUROPE region ALL country ALL etc
    - this ensures that this fact will show up in search for news about Bruge
- actors  
  - for business events this is companies, individuals involved
  - for geopolitical this is nations, trading blocs, individuals, etc
  - etc etc
- stocks likely to be impacted
  - how do we do this ?? one idea - have list of stocks that we care about -
    potentially, FTSE 350 stocks, S&P 500 companies, + oil, cryptocurrencies etc
  - having unbounded is hard but having list of companies & their stock codes
    is doable
  - also, list can be expanded in future
- sentiment
  - TODO - decide how to flesh this out

### Key Question
- do we have different tables for each category ?
  - inclined to say yes
    - relevant fields to store are seemingly different
    - also, reduces search-space - in most cases we know what category of event
      we're looking for. If we do, this makes searches more efficient. If not,  
  - but, having generic field titles as above (eg. actors etc) makes one table
    possible
    - is there any good reason for this ??

### Main Table(s)

this table shows fields and subfields :

| _id | timestamp | category | detail | region | actors | stocks impacted |
| --- | --------- | -------- | ------ | ------ | ------ | --------------- |
| none | event, source | subcategory - listed above | none | continent, region, country, county, city | none ? | market (?) |

### Lookups
Maintain multiple lookup tables that point to IDs - this will improve lookup
  speeds - tension between gains in search and spiraling memory costs.
  - but, memory cost of extra tables is quite low !

natural lookup tables come from :
  - companies / stocks
  - regions
  - people

these work by storing id of different entries which can be used to retrieve them
  efficiently
