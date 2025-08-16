"""
This module contains functions to parse the auth.log file
and extract relevant information about failed SSH login attempts.
The location of the log file is specified by the `pathToLog` variable.
"""
from geoloc import get_geo_info

def parse_log(line):
    """
    Parses the auth.log file and extracts information about failed SSH login attempts. 
    :return: ip, timestamp, user and port as strings
    """

    timestamp_str = line.split(' ')[0]
    if "invalid" in line:
        user = line.split(' ')[8]
        ip = line.split(' ')[10]
        port = line.split(' ')[12]
    else:
        user = line.split(' ')[6]
        ip = line.split(' ')[8]
        port = line.split(' ')[10]

    geo = get_geo_info(ip)
    try:
        country_long = geo.get("country_long")
        lat = geo.get("lat")
        lon = geo.get("lon")
    except KeyError:
        country_long = "Unknown"
        lat = "Unknown"
        lon = "Unknown"
    print(f"[DEBUG] ip: {ip}, user: {user}, time: {timestamp_str}, port: {port}, country: {country_long}, lat: {lat}, lon: {lon}")
    return ip, user, timestamp_str, port, country_long, lat, lon

def parse_log_lines(lines):
    """
    loads information from an array of strings and appends it to results
    :param lines: array of strings that will be analyzed
    :return: array of tuples containing the time, ip, user and
    """
    results = []
    for line in lines:
        if "Failed password" in line:
            ip, user, timestamp_str, port, country_long, lat, lon = parse_log(line)
            results.append((ip, user, timestamp_str, port, country_long, lat, lon))
    return results

