import os

from pynamodb.models import Model
from pynamodb.attributes import (UnicodeAttribute, NumberAttribute,
                                 JSONAttribute)


class Property(Model):
    class Meta:
        table_name = "property"
        region = 'us-east-1'
        write_capacity_units = 10
        read_capacity_units = 10

    id = UnicodeAttribute(hash_key=True)
    number_ratings = NumberAttribute(default=0)
    average_rating = NumberAttribute(null=True)
    zipcode = UnicodeAttribute(null=True)
    address = UnicodeAttribute(null=True)
    latitude = UnicodeAttribute(null=True)
    longitude = UnicodeAttribute(null=True)
    bedrooms = NumberAttribute(null=True)
    bathrooms = NumberAttribute(null=True)
    square_feet = NumberAttribute(null=True)
    sleeps = NumberAttribute(null=True)
    calendar = JSONAttribute()
    listing_type = UnicodeAttribute()
    country = UnicodeAttribute(default="USA")


class AirbnbProperty(Property):
    class Meta:
        table_name = "airbnb-property"
        region = 'us-east-1'
        write_capacity_units = 1
        read_capacity_units = 1

    listing_type = UnicodeAttribute(default="airbnb")


def create_tables():
    if not AirbnbProperty.exists():
        AirbnbProperty.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

if __name__ == "__main__":
    os.putenv("AWS_PROFILE", "personal")
    create_tables()
    os.unsetenv("AWS_PROFILE")
