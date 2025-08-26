import os
import mysql.connector
from dotenv import load_dotenv
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
    'database':"sshame",
}

def write_ssh_event(ip, user, timestamp_str, port, country_long, lat, lon):
    try:
        logging.info(f"Writing SSH event to MySQL.")
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO ssh_events (ip, username, ts, port, country, lat, lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (ip, user, timestamp_str, port, country_long, lat, lon)
        )

        conn.commit()
        cursor.close()
        conn.close()
        logging.info("SSH event written successfully.")
    except mysql.connector.Error as e:
        logging.error(f"Failed to write SSH event to MySQL: {e}")