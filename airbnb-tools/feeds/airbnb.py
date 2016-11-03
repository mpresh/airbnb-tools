import re
import requests
from bs4 import BeautifulSoup
from utils import remove_white_space, cleanup_int
from scraper import Scraper

ALEXA_SITE = "http://www.alexa.com/siteinfo/"
SITES = ["http://www.facebook.com", "http://www.twitter.com", "http://www.hubspot.com", "http://www.google.com", "http://www.tesla.com", "http://www.amazon.com",
         "http://www.apple.com", "http://www.amd.com", "http://www.microsoft.com", "http://www.netflix.com", "http://www.ariad.com", "https://www.gogoair.com"]

class AirbnbScraper(Scraper):

    def request_url(self, input):
        alexa_url = "{}{}".format(ALEXA_SITE, input)
        return alexa_url

    def parse(self, text):
        data = {}
        soup = BeautifulSoup(text, 'html.parser')
        global_rank = soup.find(class_="globleRank").find(class_="metrics-data")
        global_rank = remove_white_space(global_rank.text)
        data["globalRank"] = int(cleanup_int(global_rank))

        country_rank = soup.find(class_="countryRank").find(class_="metrics-data")
        country_rank = remove_white_space(country_rank.text)
        data["countryRank"] = int(cleanup_int(country_rank))
        return data

    
def main():
    s = AlexaScraper(SITES)
    s.run(display=True)
    print(s.results)
    
    
if __name__ == "__main__":
    main()
