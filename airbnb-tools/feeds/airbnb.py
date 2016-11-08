import re
import requests
from bs4 import BeautifulSoup
from scraper import Scraper

LISTINGS = ["4914702"]
AIRBNB_PHOTOS_SITE = "https://www.airbnb.com/manage-listing/{}/photos"

class AirbnbPhotosScraper(Scraper):

    def request_url(self, input):
        return AIRBNB_PHOTOS_SITE.format(input)
        
    def parse(self, text):
        data = {}
        print(text)
        return data

    
def main():
    s = AirbnbPhotosScraper(LISTINGS)
    s.run(display=False)
    print(s.results)
    
    
if __name__ == "__main__":
    main()
