from run_scrapy import run_airbnb_spider
import zipcodes 
import pprint
import time

def get_listings_by_zipcode(zipcode, state="MA", adults=None, retry=0):
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
    # all_listings = get_all_listings(zipcodes.get_all_cape_cod_zip_codes(), adults=12)
    # all_listings = get_all_listings(zipcodes.get_all_newport_zip_codes(), adults=10, state="RI")
    # all_listings = get_all_listings(zipcodes.get_all_nantucket_zip_codes(), adults=14, state="MA")
    all_listings = get_all_listings(zipcodes.get_all_marthas_vinyard_zip_codes, adults=16, state="MA")
    print(len(all_listings))
    #print(get_listings_by_zipcode("02635", adults=10))
