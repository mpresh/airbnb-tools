from run_scrapy import run_airbnb_spider
import os
import zipcodes 
import pprint
import time
import geopy
import parser
from geopy.geocoders import Nominatim
import re
from funcy import memoize
import json

@memoize
def is_listing_in_zipcode(listing_id, zipcode, retry=0):
    latitude, longitude = parser.get_listing_lat_and_long(listing_id)
    geolocator = Nominatim()
    try:
        location = geolocator.reverse("{}, {}".format(latitude, longitude))
    except geopy.exc.GeocoderTimedOut:
        time.sleep(1)
        if retry < 5:
            return is_listing_in_zipcode(listing_id, zipcode, retry=retry+1)
        else:
            return True
        
    mo = re.search("(\d\d\d\d\d), United States of America", location.address)
    if mo:
        zipcode_address = mo.group(1)
        if zipcode == zipcode_address:
            return True
        else:
            return False
    else:
        return False


def write_listings_to_file(zipcode, listings):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    listings_dir = os.path.join(root_path, "data/listings")
    if not os.path.exists(listings_dir):
        os.makedirs(listings_dir)
    zip_file = os.path.join(listings_dir, "{}.json".format(zipcode))
    with open(zip_file, "w") as f:
        f.write(json.dumps(listings))
    

def read_listings_from_file(zipcode):
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    listings_dir = os.path.join(root_path, "data/listings")
    zip_file = os.path.join(listings_dir, "{}.json".format(zipcode))
    if os.path.exists(zip_file):
        with open(zip_file) as f:
            text = f.read()
            listings = json.loads(text)
            return listings
    else:
        return False
        

        

def get_listings_by_zipcode(zipcode, state="MA", adults=None, retry=0,
                            zipcode_filter=True, refresh=False):
    if not refresh:
        listings = read_listings_from_file(zipcode)
        if listings is not False:
            return listings
    
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

    if zipcode_filter:
        listings = [listing for listing in listings if is_listing_in_zipcode(listing, zipcode)]
    write_listings_to_file(zipcode, listings)
    return listings


def get_all_listings(zip_codes_func, adults=None, state="MA", refresh=False):
    zip_codes = zip_codes_func()
    data = {}
    all_listings = set()
    all_listings_dict = {}
    towns = zip_codes.keys()
    towns.sort()
    for town in towns:
        zip_code = zip_codes[town]
        print("Town={}  Zipcode={}".format(town, zip_code))
        zip_listings = get_listings_by_zipcode(zip_code, state=state, adults=adults)
        #print("Listings ", zip_listings)
        all_listings.update(zip_listings)
        print("Found {}, Total {}".format(len(zip_listings), len(all_listings)))
        all_listings_dict["{} - {}".format(zip_code, town)] = zip_listings
        
    return all_listings_dict


if __name__ == "__main__":
    all_listings = get_all_listings(zipcodes.get_all_cape_cod_zip_codes, adults=12)
    # all_listings = get_all_listings(zipcodes.get_all_newport_zip_codes(), adults=10, state="RI")
    # all_listings = get_all_listings(zipcodes.get_all_nantucket_zip_codes(), adults=14, state="MA")
    #all_listings = get_all_listings(zipcodes.get_all_marthas_vinyard_zip_codes, adults=16, state="MA")
    #print(len(all_listings))
    #print(get_listings_by_zipcode("02635", adults=10))
