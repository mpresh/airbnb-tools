import bnbcalendar
from pprint import pprint

def calculate_total_revenue(calendar):
    total = 0
    for day, details in calendar.items():
        if details["available"] is False:
            total += details["price"]
    return total 


def calculate_revenue_for_listing(listing_id, start=None, end=None, adults=None):
    if start is None or end is None:
        calendar = bnbcalendar.get_calendar_for_next_year(property_id=listing_id)
    else:
        calendar = bnbcalendar.get_calendar_for_dates(property_id=listing_id,
                                                      start=start,
                                                      end=end)
    pprint(calendar)
    total = calculate_total_revenue(calendar)
    return total


if __name__ == "__main__":
    #total = calculate_revenue_for_listing("4914702")
    total = calculate_revenue_for_listing("16042826")
    print(total)

