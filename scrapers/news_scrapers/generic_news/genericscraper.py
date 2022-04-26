import json
import time
import requests
from datetime import datetime, timedelta
from newsplease import NewsPlease
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

INF_SCROLL = "inf_scroll"
PAGES = "pages"
SHOW_MORE = "show_more"

def main():
    # initialize browser instance
    browser = webdriver.Firefox()
    browser.implicitly_wait(10)

    with open("sources.json") as jf:
        sources = json.load(jf)

        for source in sources:
            print(f"scraping {source['source_name']}...")
            
            browser.get(source["source_url"])

            # most times these websites have a privacy permission popup which makes it
            # impossible to scroll down, so we try to click the button first
            try:
                print(source["cookie_xpath"])
                button = browser.find_element(By.XPATH, source["cookie_xpath"])
                button.click()
            except:
                print("cookie xpath failed, trying class name")
                try:
                    button = browser.find_element(By.CLASS_NAME, source["cookie_class"])
                    button.click()
                except:
                    print("class name failed, ignoring cookie popup")
            
            elem = browser.find_element(By.TAG_NAME, "body")

            n_iters = source["n_iters"]
            
            articles = []
            
            # navigate the page to get all necesary links
            if source["nav_type"] == INF_SCROLL:
                for i in range(n_iters):
                    time.sleep(1)
                    elem.send_keys(Keys.PAGE_DOWN)
                articles = browser.find_elements(By.CLASS_NAME, source["article_class"])
            elif source["nav_type"] == SHOW_MORE:
                for i in range(n_iters):
                    time.sleep(0.5)
                    show_more_button = browser.find_element(By.XPATH, source["show_more_xpath"])
                    show_more_button.click()
                articles = browser.find_elements(By.CLASS_NAME, source["article_class"])
            elif source["nav_type"] == PAGES:
                # TODO implement page navigation
                pass

            # get articles and filter by date
            for article in articles:
                url = article.get_attribute("href")
                if url:
                    news = NewsPlease.from_url(url).get_dict()
                    yesterday = datetime.today() - timedelta(days=1)
                    title = news["title"]
                    timestamp = news["date_publish"]

                    # only gets articles from the past 24 hours
                    if timestamp and timestamp >= yesterday:
                        entry = {
                            "timeStamp": datetime.strftime(yesterday, "%Y-%m-%d"),
                            "positivity": 0.0, #TODO
                            "relevance": 0.0, #TODO
                            "source": article.get_attribute("href"),
                            "category": source["category"],
                            "subcategory": source["subcategory"],
                            "detail": news["description"],
                            "actors": [], #TODO
                            "stocks": [], # TODO: Get used stocks
                            "eventRegions": []
                        }
                        r = requests.post("http://localhost:3000/events", json=entry)
                        print(title, timestamp)
                        if r.status_code != 201:
                            print(f"Status Code: {r.status_code}, Response: {r.json()}")
                        else:
                            print(f"Status Code: {r.status_code}, Success")
            print()

    browser.close()


if __name__ == "__main__":
    main()
