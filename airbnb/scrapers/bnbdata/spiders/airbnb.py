import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.conf import settings
import json
from scrapy.crawler import CrawlerProcess

settings.overrides['DEPTH_LIMIT'] = 0
#START_URLS = []
#START_URLS = ["https://www.airbnb.com/s/Cape-Cod--Barnstable-County--MA--United-States"]

class Item(scrapy.Item):
    rev_count = scrapy.Field()
    amenities = scrapy.Field()
    room_type = scrapy.Field()
    price = scrapy.Field()
    bed_type = scrapy.Field()
    person_capacity = scrapy.Field()
    cancel_policy = scrapy.Field()
    rating_communication = scrapy.Field()
    rating_cleanliness = scrapy.Field()
    rating_checkin = scrapy.Field()
    satisfaction_guest = scrapy.Field()
    instant_book = scrapy.Field()
    accuracy_rating = scrapy.Field()
    response_time = scrapy.Field()
    response_rate  = scrapy.Field()
    url = scrapy.Field()


# class BnbspiderSpider(scrapy.Spider):
class BnbSpider(scrapy.Spider):
    name = "bnbspider"
    allowed_domains = ["airbnb.com"]
    start_urls = []
    #start_urls = ["https://www.airbnb.com/s/Cape-Cod--Barnstable-County--MA--United-States"]
    #results = []
    #adults = 16

    def __init__(self, start_url='', adults=None):
        self.start_urls = [start_url]
        self.adults = adults
        print("ADULTS", self.adults)
        
    def parse(self, response):
        last_page_number = 17
        if last_page_number < 1:
            return
        else:
            if self.adults:
                offset_str = "?adults={}&section_offset=".format(self.adults)
            else:
                offset_str = "?section_offset="

            page_urls = [response.url + offset_str + str(pageNumber)
                         for pageNumber in range(last_page_number)]
            for page_url in page_urls:
                yield scrapy.Request(page_url,
                                    callback=self.parse_listing_results_page)



    def parse_listing_results_page(self, response):
        room_url_parts = set(response.xpath('//div/a[contains(@href,"rooms")]/@href').extract())
        for href in list(room_url_parts):
            url = response.urljoin(href)
            #BnbSpider.results.append(url)
            #yield scrapy.Request(url, callback=self.parse_listing_contents)
            #yield scrapy.Request(url)
            yield {"url" : url}
            
    def parse_listing_contents(self, response):
        item = Item()

        json_array = response.xpath('//meta[@id="_bootstrap-room_options"]/@content').extract()
        if json_array:
            airbnb_json_all = json.loads(json_array[0])
            airbnb_json = airbnb_json_all['airEventData']
            item['rev_count'] = airbnb_json['visible_review_count']
            item['amenities'] = airbnb_json['amenities']
            item['room_type'] = airbnb_json['room_type']
            item['price'] = airbnb_json['price']
            item['bed_type'] = airbnb_json['bed_type']
            item['person_capacity'] = airbnb_json['person_capacity']
            item['cancel_policy'] = airbnb_json['cancel_policy']
            item['rating_communication'] = airbnb_json['communication_rating']
            item['rating_cleanliness'] = airbnb_json['cleanliness_rating']
            item['rating_checkin'] = airbnb_json['checkin_rating']
            item['satisfaction_guest'] = airbnb_json['guest_satisfaction_overall']
            item['instant_book'] = airbnb_json['instant_book_possible']
            item['accuracy_rating'] = airbnb_json['accuracy_rating']
            item['response_time'] = airbnb_json['response_time_shown']
            item['response_rate'] = airbnb_json['response_rate_shown']
        item['url'] = response.url
        yield item


    def last_pagenumer_in_search(self, response):
        try:  # to get the last page number
            last_page_number = int(response
            					   .xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href')
                                   .extract()[0]
                                   .split('section_offset=')[1]
                                   )
            print(response.xpath('//ul[@class="list-unstyled"]/li[last()-1]/a/@href'))
            return last_page_number

        except KeyError:  # if there is no page number
            # get the reason from the page
            reason = response.xpath('//p[@class="text-lead"]/text()').extract()
            # and if it contains the key words set last page equal to 0
            if reason and ('find any results that matched your criteria' in reason[0]):
                logging.log(logging.DEBUG, 'No results on page' + response.url)
                return 0
            else:
            # otherwise we can conclude that the page
            # has results but that there is only one page.
                return 1


def run_scraper(start_urls, adults=None):
    global START_URLS
    
    if adults:
        start_urls[0] = start_urls[0] + "?adults={}".format(adults)

    print(start_urls)

    BnbSpider.start_urls = start_urls
    BnbSpider.results = []
    BnbSpider.adults = adults
    process = CrawlerProcess({
       'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    
    process.crawl(BnbSpider)
    process.start()
    return BnbSpider.results



if __name__ == "__main__":
    results = run_scraper(["https://www.airbnb.com/s/02635--MA--United-States"], adults=14)
    #results = run_scraper(["https://www.airbnb.com/s/02635--MA--United-States"], adults=14)
    #results = run_scraper("02635", adults=16)
    print(results)


            
