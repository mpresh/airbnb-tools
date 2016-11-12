"""
Parser to parse out an individual room page
"""

import sys
import urlparse
from urllib import urlencode
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re
from retrying import retry
from datetime import datetime, timedelta
import traceback
import dryscrape
import json


AIRBNB_LISTING_URL = "https://www.airbnb.com/rooms/{}"


def build_calendar_url(property_id, start, end, guests, key="d306zoyjsyarp7ifhu67rjxn52tv0t20"):
    start = from_datetime_torequest_date_format(start)
    end = from_datetime_torequest_date_format(end)
    
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
    
def from_datetime_torequest_date_format(dt):
    return "{}-{}-{}".format(dt.year, dt.month, dt.day)


def get_json_from_script(soup, attrs):
    attrs["type"] = "application/json"
    json_data = soup.find("script", attrs=attrs)
    
    json_data = json_data.text

    if json_data.startswith("<!--"):
        json_data = json_data[len("<!--"):]

    if json_data.endswith("-->"):
        json_data = json_data[:(len("-->") * -1)]
        
    json_data = json.loads(json_data)
    return json_data


def get_calendar_info(url):
    text = requests.get(url).text
    data = json.loads(text)
    data = data["pricing_quotes"][0]
    return data

    
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
    

def split_calendar_dates(start, end):
    td = end - start
    days = td.days
    half_days = int(days / 2)
    first_dates = (start, start + timedelta(days=half_days))
    second_dates = (start + timedelta(days=(half_days + 1)), end)
    return (first_dates, second_dates)


def get_calendar_dates(property_id, start, end, guests, minimum, key):
    url = build_calendar_url(property_id, start, end, guests, key=key)
    result = get_calendar_info(url)
    calendar = {}
    if result["available"] is False:
        first_half, second_half = split_calendar_dates(start, end)
        result_first = get_calendar_dates(property_id, first_half[0], first_half[1], guests, minimum)
        result_second = get_calendar_dates(property_id, second_half[0], second_half[1], guests, minimum)
        calendar.update(result_first)
        calendar.update(result_second)
    else:
        print(result)
        calendar = {}
    return calendar


def get_calendar(property_id="4914702", minimum=2, key="d306zoyjsyarp7ifhu67rjxn52tv0t20"):
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    end = datetime(year=int(start.year) + 1, month=start.month, day=start.day)
    guests = "4"
    return get_calendar_dates(property_id, start, end, guests, minimum, key)


@retry(wait_fixed=1000)
def get_listing_info(listing_number):
    listing_url = AIRBNB_LISTING_URL.format(listing_number)
    text = requests.get(listing_url).text
    try:
        data = parse_room_page(text)
    except Exception as e:
        print(e)
    data["listing_number"] = listing_number
    calendar = get_calendar(property_id=listing_number,
                            minimum=data["availability"],
                            key=data["key"])
    data["calendar"] = calendar
    return data


def pull_out_first_integer(text):
    mo = re.search("(\d+)", text)
    if mo:
        text = mo.group(1)

    return text


def get_key_information(soup):
    attrs = {"id": "_bootstrap-layout-init"}
    result = soup.find("meta", attrs=attrs).get("content")
    result = json.loads(result)
    return result["api_config"]["key"]


def parse_room_page(text):
    data = {}
    soup = BeautifulSoup(text, 'html.parser')
    with open("/tmp/original.txt", "w+") as f:
        f.write(text.encode("utf-8"))

    data["key"] = get_key_information(soup)
        
    try:
        
        meta_list =  list(soup.find_all("meta"))
        for meta in meta_list:
            try:
                if "latitude" in meta.get("property"):
                    data["latitude"] = meta.get("content")
                if "longitude" in meta.get("property"):
                    data["longitude"] = meta.get("content")
                if "airbedandbreakfast:rating" in meta.get("property"):
                    data["rating"] = meta.get("content")
        
            except:
                pass
                
        price = soup.find(class_="book-it").text.lower()
        start = price.find("per night")
        price = price[:start].replace("\n", "")
        mo = re.search("[$](\d*)", price)
        if mo:
            price = mo.group(1)
        data["price"] = price
        
        summary_dls = list(soup.find(class_="summary-component__dls").find("div").children)
        location = list(summary_dls[2].children)[0]
        reviews = list(summary_dls[2].children)[1]
        
        data["location"] = location.text
        reviews = reviews.text
        mo = re.search("(\d*) reviews", reviews)
        if mo:
            reviews = mo.group(1)
        else:
            reviews = None
        
        data["reviews"] = reviews
        
        profile_link = soup.find(class_="host-profile-position-sm").find("img").get("src")
        data["profile_img"] = profile_link
        
        data["superhost"] = bool(soup.find(class_="superhost"))
        
        data["title"] = soup.find(id="listing_name").text
        
        
        summary = soup.find(class_="summary-component")
        summary_details = summary.find_all(class_="col-sm-3")
        
        data["entire_place"] = bool(summary_details[0].find(class_="icon-entire-place"))
        data["entire_place"] = summary_details[0].text
        data["number_guests"] = pull_out_first_integer(summary_details[1].text)
        data["bedrooms"] = pull_out_first_integer(summary_details[2].text)
        data["beds"] = pull_out_first_integer(summary_details[3].text)
        
        
        
        details_section = soup.find(class_="details-section")
        details_div = list(details_section.children)[0]
        details_div = list(details_div.children)[0]
        details_div = list(details_div.children)[0]
        details_div = list(details_div.children)[0]
        details_children = list(details_div.children)
        
        
        for index, detail in enumerate(details_children):
            detail_text = detail.text.lower()
            
            if "bbout this listing" in detail_text:
                data["detail"] = details_children[index + 1]
        
            if "business travel" in detail_text:
                data["business"] = detail_text
        
            if "the space" in detail_text:
                data["space"] = detail_text
        
            if "amenities" in detail_text:
                data["amenities"] = detail_text
        
            if "prices" in detail_text:
                data["prices"] = detail_text
        
            if "description" in detail_text:
                data["description"] = detail_text
        
            if "house rules" in detail_text:
                data["house_rules"] = detail_text
        
            if "safety features" in detail_text:
                data["safety_features"] = detail_text
        
            if "availability" in detail_text:
                data["availability"] = pull_out_first_integer(str(detail_text))
                
        #data["details"] = details_children
    except Exception as e:
        print(e)
        raise e

    return data

    
def main():
    property_id = "4914702"
    guests = 4
    data = get_listing_info("4914702")
    #pprint(data)
    #print(get_calendar())
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day)
    end = datetime(year=int(start.year) + 1, month=start.month, day=start.day)
    url = build_calendar_url(property_id, start, end, guests)
    #data = get_calendar_info(url)
    #pprint(data)
    
if __name__ == "__main__":
    main()
