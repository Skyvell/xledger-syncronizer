from datetime import datetime


def generate_iso_8601_timestamp(remove_microseconds: bool = True):
    """
    Generates the current date and time in ISO 8601 format.
    
    Args:
        remove_microseconds (bool): If True, the microseconds part will be removed. Default is True.
    
    Returns:
        str: The current date and time in ISO 8601 format.
    """
    current_time = datetime.now()
    if remove_microseconds:
        current_time = current_time.replace(microsecond=0)
    return current_time.isoformat()


def get_current_time_for_filename():
    """
    Retrieves the current system time and formats it as a string suitable for file naming.

    This function fetches the current datetime using the system's local time and formats it
    into a compact form. The output format is 'YYYYMMDD_HH_MM_SS', where:
    - YYYY: Full year
    - MM: Month (01 to 12)
    - DD: Day of the month (01 to 31)
    - HH: Hour in 24-hour format (00 to 23)
    - MM: Minute (00 to 59)
    - SS: Second (00 to 59)
    
    The formatted time is useful for generating time-stamped filenames to ensure uniqueness or
    for sorting files chronologically based on their creation time.

    Returns:
        str: The current datetime formatted as 'YYYYMMDD_HH_MM_SS'.
    """
    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y%m%d_%H_%M_%S')
    return formatted_time