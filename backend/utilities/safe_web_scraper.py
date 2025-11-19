
class SafeWebScraper:
    def __init__(self):
        self.trusted_domains = []

    async def initialize(self):
        print("[SafeWebScraper] Service permanently disabled.")

    async def start(self):
        pass

    async def stop(self):
        pass
        
    async def search_and_learn(self, *args, **kwargs):
        print("[SafeWebScraper] search_and_learn attempted but service is disabled.")
        return {"summary": "Web scraping disabled", "sources": []}

    async def learn_topic(self, *args, **kwargs):
        print("[SafeWebScraper] learn_topic attempted but service is disabled.")
        return {"summary": "Web scraping disabled", "sources": []}

    async def scrape_url(self, *args, **kwargs):
        print("[SafeWebScraper] scrape_url attempted but service is disabled.")
        return {"content": "Web scraping disabled", "title": "Disabled"}

    def add_trusted_domain(self, *args, **kwargs):
        pass

safe_web_scraper = SafeWebScraper()
