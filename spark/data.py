

from dateutil import parser

dates = [
    "2021-05-17", #  0: first monday to start logging on
    "2021-05-18", #  1:
    "2021-05-19", #  2:
    "2021-05-20", #  3:
    "2021-05-21", #  4
    "2021-05-22", #  5: Saturday
    "2021-05-23", #  6: Sunday
    "2021-05-24", #  7: Monday (Whit monday)
    "2021-05-25", #  8:
    "2021-05-26", #  9:
    "2021-05-27", # 10: 
    "2021-05-28", # 11:
    "2021-05-29", # 12: Saturday
    "2021-05-30", # 13: Sunday
    "2021-05-31", # 14: first dayout logging
]

dates = [parser.parse(d) for d in dates]

# Get the date filters per week day.
# Consider that each filter consists of a tuple (lower & upper bound)

get_i_weekday(day: int):
    """Returns a list of indices which represent the corresponding week day."""
    b = day % 7
    return [b, b + 7]

get_name_weekday(day: int) -> str:
    """Returns the name of the weekday."""
    if day == 0:
        return "Monday"
    elif day == 1:
        return "Tuesday"
    elif day == 2:
        return "Wednesday"
    elif day == 3:
        return "Thursday"
    elif day == 4:
        return "Friday"
    elif day == 5:
        return "Saturday"
    elif day == 6:
        return "Sunday"
    else:
        raise ValueError(f"Invalid day of the week {day}")
        