from airbnb import config
from datetime import datetime, timedelta
import dryscrape
from urllib import urlencode
import requests
import json

def from_datetime_to_string(dt):
    return "{}-{}-{}".format(dt.year, str(dt.month).zfill(2), str(dt.day).zfill(2))


def make_start_to_end_date_string(start, end):
    return "{}-{}".format(from_datetime_to_string(start),
                          from_datetime_to_string(end))


def build_calendar_url(property_id, start, end, guests, key=config.key):
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
    params["guests"] = guests
    params["listing_id"] = property_id
    params["_format"] = "for_detailed_booking_info_on_web_p3_with_message_data"

    
    url = "https://www.airbnb.com/api/v2/pricing_quotes?{}".format(urlencode(params))

    return url


def get_calendar_info_old(url):
    print("URL", url)
    data = {}
    session = dryscrape.Session()
    session.visit(url)
    text = session.body()
    
    if "those dates are not available" in text.lower():
        return False
    
    soup = BeautifulSoup(text, 'html.parser')
    with open("/tmp/pricing_page.txt", "w+") as f:
        print(text)
        f.write(text.encode("utf-8"))
        
    price = soup.find(class_="book-it__price")
    data["price"] = pull_out_first_integer(price.text)    


    json_data = get_json_from_script(soup,
                                     attrs={"data-hypernova-key":
                                            "p3hero_and_slideshowbundlejs"})
    pprint(json_data)
    with open("/tmp/pricing_data.json", "w+") as logfile:
        pprint(json_data, logfile)
    sys.exit()
    

    return data


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
    second_dates = (start + timedelta(days=(half_days + 1)), end)
    return (first_dates, second_dates)



def days_difference(start, end):
    td = end - start
    return td.days


def fill_calendar_dates_with_availability_data(start, end, data):
    calendar = {}
    current_day = datetime(year=start.year, month=start.month, day=start.day)
    while current_day <= end:
        calendar[from_datetime_to_string(current_day)] = {"available": data["available"],
                                                          "price": data["average_rate_without_tax_usd"]}
        current_day = current_day + timedelta(days=1)

    return calendar


def get_calendar_dates(property_id, start, end, guests, minimum=2, key="d306zoyjsyarp7ifhu67rjxn52tv0t20"):
    url = build_calendar_url(property_id, start, end, guests, key=key)
    #print("URL", url)
    result = get_calendar_info(url)
    calendar = {}
    if result["available"] is False:
        if days_difference(start, end) > minimum:
            first_half, second_half = split_calendar_dates(start, end)
            result_first = get_calendar_dates(property_id, first_half[0], first_half[1], guests, minimum, key)
            result_second = get_calendar_dates(property_id, second_half[0], second_half[1], guests, minimum, key)

            calendar.update(result_first)
            calendar.update(result_second)
            #calendar.update(fill_calendar_dates_with_availability_data(first_half[0], first_half[1], result_first))
            #calendar.update(fill_calendar_dates_with_availability_data(second_half[0], second_half[1], result_second))
        else:
            calendar.update(fill_calendar_dates_with_availability_data(start, end, result))
    else:
        calendar.update(fill_calendar_dates_with_availability_data(start, end, result))
    return calendar


def get_calendar(property_id="4914702", minimum=2, key="d306zoyjsyarp7ifhu67rjxn52tv0t20"):
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    end = start + timedelta(days=366)
    #end = datetime(year=int(start.year) + 1, month=start.month, day=start.day)
    guests = "4"
    return get_calendar_dates(property_id, start, end, guests, minimum=minimum, key=key)


def get_calendar_for_next_year(property_id, guests=1):
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    end = start + timedelta(days=365)
    calendar = get_calendar_dates(property_id,
                                  start,
                                  end,
                                  guests,
                                  minimum=2,
                                  key=config.key)
    return calendar


