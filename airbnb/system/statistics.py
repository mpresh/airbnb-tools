import listings
import zipcodes
import finance
from pprint import pprint


# calculate earnings by zipcode
def calculate_earnings_by_zipcode(zipcodes_func, adults=12):
    properties = listings.get_all_listings(zipcodes_func, adults=12)
    for key, rooms in properties.iteritems():
        print("\n{}".format(key))
        print("Listings - {}".format(rooms))
        total = 0
        for room in rooms:
            print("Processing room {}".format(room))
            revenue = finance.calculate_revenue_for_listing(room)
            print("    Listing {} - {}".format(room, revenue))
            total += revenue
        if len(rooms) > 0:
            average = total / len(rooms)
            print("\n    Average in town {} is {}".format(key, average))

if __name__ == "__main__":
    calculate_earnings_by_zipcode(zipcodes.get_all_cape_cod_zip_codes)
