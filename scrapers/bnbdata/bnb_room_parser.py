"""
Parser to parse out an individual room page
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import re

def parse_room_page(text):
    data = {}
    soup = BeautifulSoup(text, 'html.parser')

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
    print(type(summary_details[0]))
    
    data["entire_place"] = bool(summary_details[0].find(class_="icon-entire-place"))
    data["entire_place"] = summary_details[0].text
    data["number_guests"] = summary_details[1].text
    data["bedrooms"] = summary_details[2].text
    data["beds"] = summary_details[3].text


    
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
            data["availability"] = detail_text
            
    #data["details"] = details_children

    

    



    return data

    
def main():
    text = requests.get("https://www.airbnb.com/rooms/4914702").text
    data = parse_room_page(text)
    pprint(data)
    

if __name__ == "__main__":
    main()
