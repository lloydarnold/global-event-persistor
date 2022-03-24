# Thoughts on Lloyd's thoughts on the Database Schema

### Thinking over what schema to support

The database will be used to **retrieve events related to stocks and trade based on them**. These events will primarily be from a **structured source** like GDELT, but we will also want to include other unstructured sources like Twitter and Reddit.

Things we will want to support include:

- Querying events based on
  - Stock
    - Paying special respect to crypto assets, which are the business focus of APEX:E3
  - Region 
  - Time period
  - Source (e.g. if the user wants to see "how well I can do using only events from entertainement to trade X cryptocurrency")
- Having some sort of trading signal on each event 
  - Sentiment largely plays this role, but it can be multifaceted
  - e.g. there can be negative statements about the current performance of a stock, but an optimistic view  of it for the future
  - Might want to support extending the notion of sentiment, but we first need to **figure out how to incorporate sentiment in the first place**. Our best initial approach is probably to just use whatever GDELT gives us and go with that (i.e. let the algotraders use GDELT's labels in their algorithms when backtesting).
- Possible extensions
  - Adding new sources, with a potential hierarchy structure
    - E.g. we could obtain events from Wall Street Bets, which is inside Reddit
  - Making sentiment more multifaceted

It seems to me that Lloyd's proposed schema **mostly satisfies all of the above**, so I think we can run with it, especially as an initial prototype.

### Should we even associate events with stocks?

There is an area of NLP called **named entity recognition**, whose aim is precisely to detect references to entities in text. We can somewhat crudey keep a list of relevant stocks, look for references to them using NER, and associate the news with them. 

In the end of the day, **events in the database make an association between the sentiment of the article and the entities involved in it**. Say we have an article about stock X, which says stock X is doing poorly but stock Y is doing well - the overall sentiment is negative/bearish, and yet we wouldn't want to associate a negative sentiment to Y.

With this kind of scenario in mind, it might actually be better to have a coarser analysis, and only associate stocks to events if the event is about the stock itself. Otherwise, we simply associate the stock with regions and/or entities in some mechanical way (e.g. associate a stock with the countries of the stock exchanges in which it is listed), and do the querying via this relationship.

### Dealing with location hierarchies 

One question that comes to mind about, for example, "searching for news about Bruge", is that we would need to (implicitly or explictly) know that Bruge is a city in Europe (and in Belgium, and in West Flanders). It is not clear to me how we could do this for every city in the world in a tractable way. It might be more tractable to reserve things to countries, for instance. An alternative would be to have some sort of implict (Google search-like) tool to relate city queries with countries, regions and etc., so we can look into that too.

Still, considering future expansions, it might be good to build in support for a more fine-grained description of locations associated with events.

### My take on having different tables for each category

There are 2 key issues to consider

- Usability

  - The integration between the database and the backtesting framework will be done by APEX themselves, so users won't directly have to deal with JSONs coming from our API

  - Having different schemas for different categories would lead to one of 2 scenarions

    1. Needing to merge all events together into a single container (e.g. Pandas dataframe), which would be slow and have unnecessary columns

    2. Receiving one event at a time and having a separate callback for each category

  - Which of these will occur depends on the implementation on their end, so it might be good to ask them **how the end user will access the events queried from the database(s)**

  - In case (1) happens, we should probably keep everything in the same database; otherwise it is OK to keep them separate

  - With respect to query types, I suspect there might be some kind of query optimization such that, in case the query is for a specific event category, the search space would be pruned immediately. I didn't take databases; I guess this might be the case if an internal tree representation is used, for instance. **Do any of you know if this is the case?**

- Maintainability

  - If we decide we want to change some generic field, we may have to modify it in all databases, which would be a bit cumbersome

