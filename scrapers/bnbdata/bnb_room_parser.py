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
    details_div = details_section.find("div")
    divs = details_div.find_all("div")

    

    #print(len(divs), divs[0])
    for index, div in enumerate(divs):
        print(index, div.text)

    data["description"] = divs[3].text
    data["business_travel"] = divs[8].text
    return data

    
def main():
    text = requests.get("https://www.airbnb.com/rooms/4914702").text
    data = parse_room_page(text)
    pprint(data)
    

if __name__ == "__main__":
    main()
