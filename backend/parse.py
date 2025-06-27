"""
This module contains functions to parse the auth.log file
and extract relevant information about failed SSH login attempts.
The location of the log file is specified by the `pathToLog` variable.
"""
import re
from datetime import datetime

LOG_PATTERN = re.compile(r'^(\w{3} \d{1,2} \d{2}:\d{2}:\d{2}) .* Failed password for (invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+) port (\d+)')

def parse_log(line):
    """
    matches ip, user, timestamp and port with the expressions from auth.log and extracts information.
    :param line: line from auth.log
    :return: ip, user, timestamp and port from failed login
    """
    match = LOG_PATTERN.match(line)
    if not match:
        return None  # skip unparseable line

    timestamp_str, _, user, ip, port = match.groups()

    # Reconstruct timestamp (no year, no timezone → add manually)
    full_time = datetime.strptime(timestamp_str, "%b %d %H:%M:%S")
    # Add current year (or infer from file metadata)
    full_time = full_time.replace(year=datetime.now().year)
    iso_time = full_time.isoformat() + "Z"  # UTC-style

    return ip, user, iso_time, port


def parse_log_lines(lines):
    """
    loads information from an array of strings and appends it to results
    :param lines: array of strings that will be analyzed
    :return: array of tuples containing the time, ip, user and port
    """
    results = []
    for line in lines:
        result = parse_log(line)
        if result:
            results.append(result)
    return results
