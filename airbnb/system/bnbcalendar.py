from airbnb import config
from datetime import datetime, timedelta
import dryscrape
from urllib import urlencode
import requests
import json
from pprint import pprint
import copy


def from_datetime_to_string(dt):
    return "{}-{}-{}".format(dt.year, str(dt.month).zfill(2), str(dt.day).zfill(2))


def make_start_to_end_date_string(start, end):
    return "{}-{}".format(from_datetime_to_string(start),
                          from_datetime_to_string(end))


def remove_blocked_dates(calendar):
    consecutive_count = 60
    dates = sorted(calendar.keys())

    if len(dates) < consecutive_count:
        return calendar


    new_calendar = copy.deepcopy(calendar)
    unavailable = 0
    for date in dates:
        if calendar[date]["available"] is False:
            unavailable += 1
            new_calendar[date]["available"] = True
        else:
            if unavailable > consecutive_count:
                calendar = new_calendar
            
            new_calendar = copy.deepcopy(calendar)    
            unavailable = 0
            
    if unavailable > consecutive_count:
        calendar = new_calendar
        
    return calendar


def build_calendar_url(property_id, start, end, adults, key=config.key):
    start = from_datetime_to_string(start)
    end = from_datetime_to_string(end)
    
    params = {}
    params["locale"] = "en"
    params["currency"] = "USD"
    params["key"] = key
    #params["_p3_impression_id"] = "p3_1478914996_rpkXwODnQeHvhYUk"
    params["check_in"] = start
    params["check_out"] = end
    #params["_parent_request_uuid"] = "795e2598-7da1-41d7-b5ff-dd00b1992ae9"
    params["_intents"] = "p3_book_it"
    params["_interaction_type"] = "pageload"
    params["adults"] = adults
    params["listing_id"] = property_id
    params["_format"] = "for_detailed_booking_info_on_web_p3_with_message_data"

    
    url = "https://www.airbnb.com/api/v2/pricing_quotes?{}".format(urlencode(params))

    return url


def get_calendar_info(url):
    text = requests.get(url).text
    data = json.loads(text)
    data = data["pricing_quotes"][0]
    return data
       

def split_calendar_dates(start, end):
    td = end - start
    days = td.days
    half_days = int(days / 2)
    first_dates = (start, start + timedelta(days=half_days))
    second_dates = (start + timedelta(days=(half_days)), end)
    return (first_dates, second_dates)


def days_difference(start, end):
    td = end - start
    return td.days


def fill_calendar_dates_with_availability_data(start, end, data):
    calendar = {}
    #pprint(data)
    current_day = datetime(year=start.year, month=start.month, day=start.day)
    #pprint(data)
    available = data["available"]
    if "minimum stay is" in data["localized_unavailability_message"].lower():
        available = True
        
    while current_day <= end:
        nightly_rate = int(float(data["base_price_usd"])/float(data["nights"]))
        calendar[from_datetime_to_string(current_day)] = {"available": available,
                                                          "price": nightly_rate}
        current_day = current_day + timedelta(days=1)

    return calendar


def get_calendar_dates(property_id, start, end, adults, minimum=1, key="d306zoyjsyarp7ifhu67rjxn52tv0t20"):
    minimum_booking = 10
    time_diff = days_difference(start, end)
    url = build_calendar_url(property_id, start, end, adults, key=key)
    result = get_calendar_info(url)
    #print("URL", url)
    
    unavailable_message = result["localized_unavailability_message"]
    
    #pprint(result)
    calendar = {}
    if result["available"] is False:
        if days_difference(start, end) > minimum_booking:
            first_half, second_half = split_calendar_dates(start, end)
            result_first = get_calendar_dates(property_id, first_half[0], first_half[1], adults, minimum, key)
            result_second = get_calendar_dates(property_id, second_half[0], second_half[1], adults, minimum, key)

            calendar.update(result_first)
            calendar.update(result_second)
            #calendar.update(fill_calendar_dates_with_availability_data(first_half[0], first_half[1], result_first))
            #calendar.update(fill_calendar_dates_with_availability_data(second_half[0], second_half[1], result_second))
        elif days_difference(start, end) < minimum_booking and days_difference(start, end) >  1:
            for day in range(0, days_difference(start, end)):
                #print("DAY", day, days_difference(start, end))
                start_day = start + timedelta(days=day)
                end_day = start + timedelta(days=day+1)
                day_result = get_calendar_dates(property_id,
                                                start_day,
                                                end_day,
                                                adults,
                                                minimum,
                                                key)
                calendar.update(day_result)
        else:
            calendar.update(fill_calendar_dates_with_availability_data(start, end, result))
    else:
        calendar.update(fill_calendar_dates_with_availability_data(start, end, result))
    #print(start, end, calendar)
    return remove_blocked_dates(calendar)


def get_calendar(property_id="4914702", minimum=2, key="d306zoyjsyarp7ifhu67rjxn52tv0t20"):
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    end = start + timedelta(days=366)
    adults = "4"
    return get_calendar_dates(property_id, start, end, adults, minimum=minimum, key=key)


def get_calendar_for_next_year(property_id, adults=1):
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    end = start + timedelta(days=365)
    calendar = get_calendar_dates(property_id,
                                  start,
                                  end,
                                  adults,
                                  minimum=2,
                                  key=config.key)
    return calendar


def get_calendar_for_next_days(property_id, adults=1, days=20):
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    end = start + timedelta(days=days)
    calendar = get_calendar_dates(property_id,
                                  start,
                                  end,
                                  adults,
                                  minimum=2,
                                  key=config.key)
    return calendar


def get_calendar_for_dates(property_id, adults=1, start=None, end=None):
    calendar = get_calendar_dates(property_id,
                                  start,
                                  end,
                                  adults,
                                  minimum=2,
                                  key=config.key)
    return calendar


    
if __name__ == "__main__":
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    start = start + timedelta(days=21)
    end = start + timedelta(days=5)
    #pprint(get_calendar_for_next_year(property_id="4914702"))
    print(start, end)
    pprint(get_calendar_for_dates(property_id="16042826", start=start, end=end))
