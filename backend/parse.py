"""
This module contains functions to parse the auth.log file
and extract relevant information about failed SSH login attempts.
The location of the log file is specified by the `pathToLog` variable.
"""
from geoloc import get_geo_info
from database import write_ssh_event
import logging
import os
import re
from dotenv import load_dotenv

load_dotenv()

level_name = os.getenv("LOGGING_LEVEL", "INFO").upper()
level = getattr(logging, level_name, logging.INFO) 

logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s")


def parse_log(line):
    """
    Parses the auth.log file and extracts information about failed SSH login attempts. 
    :return: ip, timestamp, user and port as strings
    """
    RE_TS   = re.compile(r'^(?P<ts>\d{4}-\d{2}-\d{2}T[^\s]+)')
    RE_USER = re.compile(r'Failed password for (?:invalid user |unknown user )?(?P<user>\S+)')
    RE_IP   = re.compile(r'\bfrom\s+(?P<ip>(?:\d{1,3}\.){3}\d{1,3}|[0-9A-Fa-f:]+)\b')
    RE_PORT = re.compile(r'\bport\s+(?P<port>\d+)\b')

    m = RE_TS.search(line)
    timestamp_str = m.group('ts') if m else None

    # User
    m = RE_USER.search(line)
    user = m.group('user') if m else None

    # IP
    m = RE_IP.search(line)
    ip = m.group('ip') if m else None

    # Port
    m = RE_PORT.search(line)
    port = m.group('port') if m else None

    if not ip:
        logging.debug(f"IP nicht gefunden in Zeile: {line.strip()}")
        return None, None, None, None, None, None, None

    geo = get_geo_info(ip)
    try:
        country_long = geo.get("country_long")
        lat = geo.get("lat")
        lon = geo.get("lon")
    except KeyError:
        country_long = None
        lat = None
        lon = None
    logging.debug(f"ip: {ip}, user: {user}, time: {timestamp_str}, port: {port}, country: {country_long}, lat: {lat}, lon: {lon}")
    return ip, user, timestamp_str, port, country_long, lat, lon
def parse_log_lines(lines):
    """
    loads information from an array of strings and appends it to results
    :param lines: array of strings that will be analyzed
    :return: array of tuples containing the time, ip, user and
    """
    for line in lines:
        if "Failed password" in line and not "message repeated" in line:
            ip, user, timestamp_str, port, country_long, lat, lon = parse_log(line)
            write_ssh_event(ip, user, timestamp_str, port, country_long, lat, lon)

