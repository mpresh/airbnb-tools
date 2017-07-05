"""
Parser to parse out an individual room page
"""

import sys
import urlparse
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re
from retrying import retry
import traceback
import json


AIRBNB_LISTING_URL = "https://www.airbnb.com/rooms/{}"

    
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


@retry(wait_fixed=1000)
def get_listing_info(listing_number):
    listing_url = AIRBNB_LISTING_URL.format(listing_number)
    text = requests.get(listing_url).text
    try:
        data = parse_room_page(text)
    except Exception as e:
        print(e)
    print("OOO", data["key"], data["min_nights"])
    data["listing_number"] = listing_number
    calendar = get_calendar(property_id=listing_number,
                            minimum=data["min_nights"],
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
        
    try:

        data["key"] = get_key_information(soup)
        json_data = get_json_from_script(soup,
                                         attrs={"data-hypernova-key":
                                                "p3hero_and_slideshowbundlejs"})
        json_data = json_data["slideshowProps"]["listing"]
        #pprint(json_data)
        #print(type(json_data))
        #print(json_data.keys())
        data.update(json_data)
        
        
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
        
        #summary_dls = list(soup.find(class_="summary-component__dls").find("div").children)
        #location = list(summary_dls[2].children)[0]
        #reviews = list(summary_dls[2].children)[1]
        #data["location"] = location.text
        #reviews = reviews.text
        #mo = re.search("(\d*) reviews", reviews)
        #if mo:
        #    reviews = mo.group(1)
        #else:
        #    reviews = None
        #
        #data["reviews"] = reviews

        
        #profile_link = soup.find(class_="host-profile-position-sm").find("img").get("src")
        #data["profile_img"] = profile_link
        
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
            
            if "about this listing" in detail_text:
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
                
    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
        raise e

    return data

    
if __name__ == "__main__":
    main()
