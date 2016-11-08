import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class AirbnbSpider(CrawlSpider):
    name = 'airbnb.com'
    allowed_domains = ['airbnb.com']
    #start_urls = ['http://www.airbnb.com/s/cotuit--ma']
    start_urls = ['http://www.airbnb.com/s/cape-cod--ma']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor(allow=('page', ))),

        # Extract links matching 'item.php' and parse them with the spider's method parse_item
        Rule(LinkExtractor(allow=('rooms', )), callback='parse_item'),
    )

    def parse_item(self, response):
        self.logger.info('room page! %s', response.url)
        #item = scrapy.Item()
        #item['id'] = response.xpath('//td[@id="item_id"]/text()').re(r'ID: (\d+)')
        #item['name'] = response.xpath('//td[@id="item_name"]/text()').extract()
        #item['description'] = response.xpath('//td[@id="item_description"]/text()').extract()
        #return item
        return {"url": response.url}
