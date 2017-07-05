def calculate_total_income(calendar):
    total = 0
    for day, details in calendar.items():
        if details["available"] is False:
            total += details["price"]
    return total * .8
