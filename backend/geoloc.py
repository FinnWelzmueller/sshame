import os
import mysql.connector
from dotenv import load_dotenv
import time
load_dotenv()

MYSQL_CONFIG = {
    'host': 'mysql', 
    'user': os.getenv("MYSQL_USER"),
    'password': os.getenv("MYSQL_PASSWORD"),
    'database': 'geoip',
}

DEFAULT_GEO = {
    "country_long": "Unknown",
    "lat": None,
    "lon": None
}

def get_geo_info(ip_str, retries=10, delay=10):
    print(f"[DEBUG] Raw IP from log: '{ip_str}'")
    ip_int = ip_to_int(ip_str)
    print(f"[DEBUG] Converted to int: {ip_int}")

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
            print(f"[MySQL] Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)

    print("[MySQL] All connection attempts failed.")
    return DEFAULT_GEO.copy()


def ip_to_int(ip_str):
    parts = [int(part) for part in ip_str.split('.')]
    return (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + parts[3]
