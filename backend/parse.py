"""
This module contains functions to parse the auth.log file
and extract relevant information about failed SSH login attempts.
The location of the log file is specified by the `pathToLog` variable.
"""
pathToLog = "../auth.log"

def parse_log():
    """
    Parses the auth.log file and extracts information about failed SSH login attempts. 
    Each tuple is structured as (time, username, IP address, port).
    :return: A list of tuples containing the time, username, IP adress and port of each failed attempt.
    """
    with open(pathToLog, 'r') as file:
        content = file.readlines()
    info = []
    failed = [ele for ele in content if "Failed password" in ele]

    for ele in failed:
        element = dict()

        element["time"] = ele.split(' ')[0]
        if "invalid" in ele:
            element["name"] = ele.split(' ')[8]
            element["ip"] = ele.split(' ')[10]
            element["port"] = ele.split(' ')[12]
        else:
            element["name"] = ele.split(' ')[6]
            element["ip"] = ele.split(' ')[8]
            element["port"] = ele.split(' ')[10]
        info.append(element)
    return info

