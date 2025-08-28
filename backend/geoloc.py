import os
import mysql.connector
from dotenv import load_dotenv
import time
import logging

load_dotenv()
level_name = os.getenv("LOGGING_LEVEL", "INFO").upper()
level = getattr(logging, level_name, logging.INFO) 

logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s")

MYSQL_CONFIG = {
    'host': 'mysql', 
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': "sshame",
}

DEFAULT_GEO = {
    "country_long": None,
    "lat": None,
    "lon": None
}

def get_geo_info(ip_str: str, retries=10, delay=10):
    logging.debug(f"Raw IP from log: '{ip_str}'")
    ip_int = ip_to_int(ip_str)
    logging.debug(f"-> Converted to int: {ip_int}")

    for attempt in range(retries):
        try:
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT country_long, lat, lon
                FROM ip_locations
                WHERE %s BETWEEN ip_from AND ip_to
                """,
                (ip_int,)
            )
            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return row
            else:
                return DEFAULT_GEO.copy()

        except mysql.connector.Error as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)

    logging.error("All connection attempts failed.")
    return DEFAULT_GEO.copy()


def ip_to_int(ip_str: str)  -> int:
    parts = [int(part) for part in ip_str.split('.')]
    return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
