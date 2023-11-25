import logging
from typing import Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def attach_symbol(salary: str)-> str:
    """
    Attaches the "$" symbol to values in USD
    """
    salary = salary.replace("\u2013", "-")
    if salary and salary[0].isdigit():
        salary = "-".join("$"+s for s in salary.split('-'))
    return salary

def convert_string_to_datetime(time_string: str)-> Optional[datetime]:
    """This function takes a string representing a time difference in the format "X units ago" (e.g., "12 hours ago") 
    as input. It parses the input string, extracts the numerical value and time unit, and calculates the datetime by 
    subtracting the corresponding timedelta from the current date and time. The function returns a datetime object 
    representing the computed date and time.
    """
    value, unit, _ = time_string.split()
    value = int(value)

    units_mapping = {
        'second': timedelta(seconds=1),
        'seconds': timedelta(seconds=1),
        'minute': timedelta(minutes=1),
        'minutes': timedelta(minutes=1),
        'hour': timedelta(hours=1),
        'hours': timedelta(hours=1),
        'day': timedelta(days=1),
        'days': timedelta(days=1),
        'week': timedelta(weeks=1),
        'weeks': timedelta(weeks=1),
    }

    if unit in units_mapping:
        delta = units_mapping[unit] * value
        result_datetime = datetime.now() - delta
        return result_datetime
    else:
        logger.error("Unsupported time unit")

def clean_data(dirty_data: str or list) -> str:
    """The `clean_data` function takes in a string or a list of strings and returns a cleaned version of
    the input by removing extra whitespace and joining the strings with a "|" separator if the input is
    a list.

    Parameters
    ----------
    dirty_data : str or list
        The `dirty_data` parameter can be either a string or a list. If it is a string, the function will
    remove any extra whitespace and return the cleaned string. If it is a list, the function will clean
    each element of the list by removing extra whitespace, and then join the cleaned elements

    Returns
    -------
        The function `clean_data` returns a cleaned version of the input `dirty_data`. If `dirty_data` is a
    string, it removes any extra whitespace and returns the cleaned string. If `dirty_data` is a list of
    strings, it removes extra whitespace from each string in the list, joins them with a "|" separator,
    and returns the cleaned string.

    """
    if isinstance(dirty_data, str):
        dirty_data = " ".join(dirty_data.split()).strip()
        return dirty_data

    dirty_data = "\n\n- ".join(dirty_data)
    return dirty_data