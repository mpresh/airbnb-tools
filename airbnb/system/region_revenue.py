import zipcodes
import listings
import bnbcalendar
import finance
from pprint import pprint

def region_average_revenue(zipcodes_func, adults=16, state="MA"):
    rooms = listings.get_all_listings(zipcodes_func, adults=adults, state=state)
    #rooms = ["4914702", "16042826"]
    for room in rooms:
        print("Getting calendar for {}".format(room))
        calendar = bnbcalendar.get_calendar_for_next_year(room, adults=adults-3)
        total_revenue = finance.calculate_total_revenue(calendar)
        print("listing {}   revenue {}".format(room, total_revenue))

        
if __name__ == "__main__":
    region_average_revenue(zipcodes.get_all_cape_cod_zip_codes)

