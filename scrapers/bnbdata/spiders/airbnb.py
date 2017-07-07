import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.conf import settings
settings.overrides['DEPTH_LIMIT'] = 0

START_URLS = ["https://www.airbnb.com/s/Cape-Cod--Barnstable-County--MA--United-States"]

class AirbnbSpider(CrawlSpider):
    name = 'airbnb.com'
    allowed_domains = ['airbnb.com']
    start_urls = START_URLS
    results = []
    
    rules = (
        Rule(LinkExtractor(allow=(".*homes.*", )), ),
        Rule(LinkExtractor(allow=('rooms', )), callback='parse_item'),
    )

    
    def parse_item(self, response):
        if "room" in response.url:
            #self.logger.info('room page! %s', response.url)
            #print("room", response.url)
            AirbnbSpider.results.append(response.url)
            
        return {"url": response.url}


def run_scraper(start_urls):
    global START_URLS
    START_URLS = start_urls
    AirbnbSpider.results = []
    process = CrawlerProcess({
       'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    process.crawl(AirbnbSpider)
    process.start()
    return AirbnbSpider.results
    
    
    
if __name__ == "__main__":
    results = run_scraper(START_URLS)
    print(results)
