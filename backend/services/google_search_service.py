
class GoogleSearchService:
    def __init__(self):
        pass

    async def initialize(self):
        print("[GoogleSearch] Service permanently disabled.")

    async def search(self, *args, **kwargs):
        return []

google_search_service = GoogleSearchService()
