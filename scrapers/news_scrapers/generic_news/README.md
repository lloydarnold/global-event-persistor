# Generic news scrapers

The design of this scraper is so that a separate scraper can be created for each content type. The websites to be crawled are given in `news-please-config/config.cfg`.

You will need to install the modified version of NewsPlease

```
# NOT in the global-event-persistor directory
git clone https://github.com/FelipeNuti/news-please.git
cd news-please
conda activate scraperenv # same environment as other scrapers
pip install .
```

# To run database handler
All scrapers should forward their scraped articles to an API written in `db_handler.py`. This API uses the `test-lm` conda environment, the same as the inference API in the `language-models` folder.

```
cd (. . .)/global-event-persistor/scrapers/news_scrapers/generic_news
source setup.bash
flask run --port 8081
```

# Configurations

This refers to the `config.cfg` file.
Use the `SitemapCrawler`. The endpoint for the database handler and the category that is being scraped need to be specified:

```
[GlobalDataPersister]
category = "SPO"
db_endpoint = "http://127.0.0.1:8081/push_events"
```

ITEM_PIPELINES also need to be adjusted:
```
ITEM_PIPELINES = {'newsplease.pipeline.pipelines.GlobalDataPersister':200,
                  'newsplease.pipeline.pipelines.ArticleMasterExtractor':100,
                  #'newsplease.pipeline.pipelines.HtmlFileStorage':200,
                  #'newsplease.pipeline.pipelines.JsonFileStorage':300
                  }
```

The following refers to `sitelist.hjson`.
Here you can specify the url's to be scraped, as well as the subdomains you want to scrape from. For news websites, for example, you can restrict to links about a given category (e.g. sports). This is done in the `restrict_domains_to` heuristic. Only links whose prefix is one of the values for this heuristic will be scraped.

```
{
      # Start crawling from faz.net
      "url": "https://www.bbc.com/sport",

      # Overwrite the default crawler and use th RecursiveCrawler instead
      "crawler": "SitemapCrawler",

      "overwrite_heuristics": {
        "meta_contains_article_keyword": true,
        "og_type": true,
        "is_not_from_subdomain": true,
        "restrict_domains_to": ["https://www.bbc.com/sport", "https://www.bbc.co.uk/sport"] 
      },

      "pass_heuristics_condition": "restrict_domains_to and og_type"
    },
```

E.g. "https://www.bbc.com/ukchina" will not be scraped; "https://www.bbc.com/sport/articles/c4n9ggwz90go" will.

# To run
```
news-please-gdpc -c news-please-config/
```