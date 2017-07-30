from run_scrapy import run_airbnb_spider
import zipcodes 
import pprint
import time
import geopy
import parser
from geopy.geocoders import Nominatim
import re
    
def is_listing_in_zipcode(listing_id, zipcode):
    latitude, longitude = parser.get_listing_lat_and_long(listing_id)
    geolocator = Nominatim()
    location = geolocator.reverse("{}, {}".format(latitude, longitude))
    mo = re.search("(\d\d\d\d\d), United States of America", location.address)
    if mo:
        zipcode = mo.group(1)
        return zipcode
    else:
        print(location.address)
        return False


def get_listings_by_zipcode(zipcode, state="MA", adults=None, retry=0, zipcode_filter=True):
    start_url = "https://www.airbnb.com/s/{}--{}--United-States".format(zipcode, state)
    try:
        listings = run_airbnb_spider(start_url=start_url, adults=adults)
    except ValueError:
        time.sleep(2)
        if retry == 5:
            listings = []
        else:
            listings = get_listings_by_zipcode(zipcode,
                                               state=state,
                                               adults=adults,
                                               retry=retry+1)

    print("Listings found in zipcode {}  #={}".format(zipcode, len(listings)))
    if zipcode_filter:
        listings = [listing for listing in listings if is_listing_in_zipcode(listing, zipcode)]
    print("Listings found in zipcode filtered {}  #={}".format(zipcode, len(listings)))
    return listings


def get_all_listings(zip_codes_func, adults=None, state="MA"):
    zip_codes = zip_codes_func()
    data = {}
    all_listings = set()
    towns = zip_codes.keys()
    towns.sort()
    for town in towns:
        zip_code = zip_codes[town]
        print("Town={}  Zipcode={}".format(town, zip_code))
        zip_listings = get_listings_by_zipcode(zip_code, state=state, adults=adults)
        #print("Listings ", zip_listings)
        all_listings.update(zip_listings)
        print("Found {}, Total {}".format(len(zip_listings), len(all_listings)))

    return all_listings


if __name__ == "__main__":
    all_listings = get_all_listings(zipcodes.get_all_cape_cod_zip_codes, adults=12)
    # all_listings = get_all_listings(zipcodes.get_all_newport_zip_codes(), adults=10, state="RI")
    # all_listings = get_all_listings(zipcodes.get_all_nantucket_zip_codes(), adults=14, state="MA")
    #all_listings = get_all_listings(zipcodes.get_all_marthas_vinyard_zip_codes, adults=16, state="MA")
    #print(len(all_listings))
    #print(get_listings_by_zipcode("02635", adults=10))
