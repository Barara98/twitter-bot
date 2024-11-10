import requests
from datetime import datetime, timedelta
from celebrity_db import CelebrityDatabase


class CelebrityArticleFetcher:
    def __init__(self):
        self.celebrity_types = {"Q5", "Q33999", "Q488111", "Q483501"} 
        self.articles = []
        self.celebrities = []
        self.database = CelebrityDatabase()  

    def get_yesterdays_top_articles(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/en.wikipedia.org/all-access/{yesterday}"

        headers = {
            'User-Agent': 'MyApp/1.0 (http://mywebsite.com/contact)'  
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            self.articles = [item['article'] for item in data['items'][0]['articles'][:75]]  
        except requests.exceptions.RequestException as e:
            print(f"Error fetching top articles: {e}")

    def get_wikidata_id(self, title):
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={title}&prop=pageprops&format=json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_data in pages.items():
                if "pageprops" in page_data and "wikibase_item" in page_data["pageprops"]:
                    wikidata_id = page_data["pageprops"]["wikibase_item"]
                    return wikidata_id
        except requests.exceptions.RequestException as e:
            print(f"Error fetching Wikidata ID for '{title}': {e}")
        return None

    def is_human_or_celebrity(self, wikidata_id):
        url = f"https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            entity_data = data.get("entities", {}).get(wikidata_id, {})
            claims = entity_data.get("claims", {})


            for prop in ["P31", "P106"]:
                if prop in claims:
                    for claim in claims[prop]:
                        if claim["mainsnak"]["datavalue"]["value"]["id"] in self.celebrity_types:
                            return True
        except requests.exceptions.RequestException as e:
            print(f"Error checking if '{wikidata_id}' is a celebrity: {e}")
        return False

    def format_title(self, title):
        title = title.replace('_', ' ')
        title = title.split('(')[0].strip() 
        return title

    def fetch_celebrities(self):
        self.celebrities = []  
        self.get_yesterdays_top_articles()

        for title in self.articles:
            celeb = self.database.exists(title)
            if celeb:
                if celeb[1]:
                    self.celebrities.append((self.format_title(title), self.database.get_twitter_account(title)))
                else:
                    continue
            else:
                wikidata_id = self.get_wikidata_id(title)
                if wikidata_id and self.is_human_or_celebrity(wikidata_id):
                    self.celebrities.append((self.format_title(title), self.database.get_twitter_account(title)))
                    self.database.add_to_database(title, wikidata_id, True)
                else:
                    self.database.add_to_database(title, wikidata_id, False)
            if len(self.celebrities) >= 24:
                break

        return self.celebrities


