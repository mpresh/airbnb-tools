from run_scrapy import run_airbnb_spider
from zipcodes import get_all_cape_cod_zip_codes
import pprint


def get_listings_by_zipcode(zipcode, state="MA", adults=None):
    start_url = "https://www.airbnb.com/s/{}--{}--United-States".format(zipcode, state)
    listings = run_airbnb_spider(start_url=start_url, adults=adults)
    return listings


def get_all_cape_listings(adults=None):
    cape_listings = set()
    zip_codes =  get_all_cape_cod_zip_codes()
    towns = zip_codes.keys()
    towns.sort()
    for town in towns:
        zip_code = zip_codes[town]
        print("Town={}  Zipcode={}".format(town, zip_code))
        zip_listings = get_listings_by_zipcode(zip_code, adults=adults)
        print("Listings ", zip_listings)
        cape_listings.update(zip_listings)
        print("Found {}, Total {}".format(len(zip_listings), len(cape_listings)))

    return cape_listings


if __name__ == "__main__":
    all_listings = get_all_cape_listings(adults="16")
    print(len(all_listings))
    #print(get_listings_by_zipcode("02635", adults=10))
