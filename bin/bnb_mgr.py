"""
Tool to manage bnb commands.

Usage:
  
"""
from airbnb.system import calendar
from airbnb.system import config

if __name__ == "__main__":
    print(calendar.get_calendar_for_next_year(config.sample_property_id))
