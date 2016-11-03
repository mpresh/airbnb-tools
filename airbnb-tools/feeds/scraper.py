import requests

class Scraper:
    
    def __init__(self, data):
        self.data = data
        self.results = {}
        
    def run(self, display=False):
        results = {}
        for result in self.scrape():
            if display:
                print(result)
            print(result)
            self.results.update(result)

    def parse(self, text):
        return {}

    def request_url(self, item):
        """ Should be overriden """
        return item

    def get_key(self, item):
        """ Should be overriden """
        return item

    def make_request(self, request_item):
        result = requests.get(request_url)
        return result.text
        
    def scrape(self):
        for item in self.data:
            request_url = self.request_url(item)
            result = self.make_request(request_url)
            item_key = self.get_key(item)
            yield {item_key: self.parse(result)}
